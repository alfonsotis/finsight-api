import os
import yfinance as yf
from celery import shared_task
from openai import OpenAI
from .models import AnalysisTask

# Inicializamos el cliente de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@shared_task
def analyze_portfolio_task(db_task_id):
    try:
        task = AnalysisTask.objects.get(id=db_task_id)
        task.status = 'PROCESSING'
        task.save()
        
        tickers_list = task.portfolio.tickers
        tickers_str = " ".join(tickers_list)
        
        # 1. Bajar datos duros (Yahoo)
        data = yf.download(tickers_str, period="1mo", group_by='ticker')
        
        raw_metrics = []
        for ticker in tickers_list:
            ticker_data = data[ticker] if len(tickers_list) > 1 else data
            start_price = ticker_data['Close'].iloc[0]
            end_price = ticker_data['Close'].iloc[-1]
            perf = ((end_price - start_price) / start_price) * 100
            raw_metrics.append(f"{ticker}: {perf:+.2f}%")
        
        # 2. Llamada al LLM (El "Cerebro")
        prompt = f"Actúa como un analista cuantitativo de un Hedge Fund. He analizado el rendimiento mensual de este portafolio: {', '.join(raw_metrics)}. Redacta un insight ejecutivo, profesional y directo (máximo 3 párrafos) explicando el posible contexto de mercado detrás de estos movimientos."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Usamos la versión rápida y económica
            messages=[
                {"role": "system", "content": "Eres un analista financiero experto."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 3. Guardar el análisis inteligente
        task.llm_insight = response.choices[0].message.content
        task.status = 'COMPLETED'
        task.save()
        
    except Exception as e:
        task.status = 'FAILED'
        task.llm_insight = f"Error en el pipeline financiero: {str(e)}"
        task.save()