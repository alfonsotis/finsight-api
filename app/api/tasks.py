import os
import yfinance as yf
from celery import shared_task
from openai import OpenAI
from .models import AnalysisTask

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@shared_task
def analyze_portfolio_task(db_task_id):
    try:
        task = AnalysisTask.objects.get(id=db_task_id)
        task.status = 'PROCESSING'
        task.save()
        
        tickers_list = task.portfolio.tickers
        tickers_str = " ".join(tickers_list)
        
        # 1. Download price data
        data = yf.download(tickers_str, period="1mo", group_by='ticker')
        
        raw_metrics = []
        real_news_context = []
        
        for ticker in tickers_list:
            ticker_data = data[ticker] if len(tickers_list) > 1 else data
            start_price = ticker_data['Close'].iloc[0]
            end_price = ticker_data['Close'].iloc[-1]
            perf = ((end_price - start_price) / start_price) * 100
            raw_metrics.append(f"{ticker}: {perf:+.2f}%")
            
            # 2. Download news
            ticker_obj = yf.Ticker(ticker)
            recent_news = ticker_obj.news[:3]
            for news_item in recent_news:
                # THE FIX IS HERE: We extract the title from the sub-dictionary 'content'
                title = news_item.get('content', {}).get('title') or news_item.get('title', '')
                
                # We only add it if it actually contains text
                if title:
                    real_news_context.append(f"Noticia sobre {ticker}: {title}")
        
        # --- THE DEFENSIVE WORKAROUND ---
        noticias_str = chr(10).join(real_news_context) if real_news_context else "NINGUNA NOTICIA DISPONIBLE"
        
        # 3. The Anti-Hallucination Prompt (Strict RAG)
        prompt = f"""
        Actúa como un analista cuantitativo.
        Rendimiento mensual: {', '.join(raw_metrics)}.
        
        TITULARES DE NOTICIAS REALES DE HOY:
        {noticias_str}
        
        REGLA ESTRICTA 1: Basa tu análisis EXCLUSIVAMENTE en los titulares proporcionados. NO INVENTES factores macroeconómicos, ni de tasas de interés, ni tendencias de digitalización si no están explícitamente en los titulares.
        REGLA ESTRICTA 2: Debes citar textualmente el titular de la noticia que justifica tu análisis. Si la lista de titulares está vacía o dice "NINGUNA NOTICIA DISPONIBLE", DEBES responder exactamente esto: "No hay noticias recientes suficientes para justificar este movimiento", y detenerte ahí.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista financiero experto. Odias la especulación y solo hablas con base en hechos demostrables."},
                {"role": "user", "content": prompt}
            ]
        )
        
        task.llm_insight = response.choices[0].message.content
        task.status = 'COMPLETED'
        task.save()
        
    except Exception as e:
        task.status = 'FAILED'
        task.llm_insight = f"Error: {e!s}"
        task.save()