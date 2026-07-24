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
        
        # 1. Bajar datos de precios
        data = yf.download(tickers_str, period="1mo", group_by='ticker')
        
        raw_metrics = []
        real_news_context = [] # <--- Aquí guardaremos la realidad
        
        for ticker in tickers_list:
            ticker_data = data[ticker] if len(tickers_list) > 1 else data
            start_price = ticker_data['Close'].iloc[0]
            end_price = ticker_data['Close'].iloc[-1]
            perf = ((end_price - start_price) / start_price) * 100
            raw_metrics.append(f"{ticker}: {perf:+.2f}%")
            
            # 2. Descargar noticias reales recientes del ticker
            ticker_obj = yf.Ticker(ticker)
            recent_news = ticker_obj.news[:3] # Tomamos las 3 últimas noticias
            for news_item in recent_news:
                real_news_context.append(f"Noticia sobre {ticker}: {news_item.get('title', '')}")
        
        # 3. El Prompt Antialucinaciones (RAG)
        prompt = f"""
        Actúa como un analista cuantitativo.
        Rendimiento mensual: {', '.join(raw_metrics)}.
        
        TITULARES DE NOTICIAS REALES DE HOY:
        {chr(10).join(real_news_context)}
        
        REGLA ESTRICTA: Redacta un insight ejecutivo (máximo 2 párrafos) explicando el rendimiento. 
        BASA TU ANÁLISIS EXCLUSIVAMENTE en los titulares proporcionados. Si los titulares no explican la subida/bajada, indica que el movimiento es por factores de mercado no reportados recientemente. NO INVENTES razones.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista financiero experto. Odias la especulación y solo hablas con base en hechos."},
                {"role": "user", "content": prompt}
            ]
        )
        
        task.llm_insight = response.choices[0].message.content
        task.status = 'COMPLETED'
        task.save()
        
    except Exception as e:
        task.status = 'FAILED'
        task.llm_insight = f"Error: {str(e)}"
        task.save()