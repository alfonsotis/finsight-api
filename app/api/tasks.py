import yfinance as yf
from celery import shared_task
from .models import AnalysisTask

@shared_task
def analyze_portfolio_task(db_task_id):
    try:
        task = AnalysisTask.objects.get(id=db_task_id)
        task.status = 'PROCESSING'
        task.save()
        
        # 1. Preparar los tickers (ej: ["AAPL", "MSFT"] -> "AAPL MSFT")
        tickers_list = task.portfolio.tickers
        tickers_str = " ".join(tickers_list)
        
        # 2. Descargar datos reales de Yahoo Finance (el último mes)
        data = yf.download(tickers_str, period="1mo", group_by='ticker')
        
        # 3. Construir el insight analizando los datos
        insights = []
        insights.append(f"Análisis procesado para {len(tickers_list)} activos en el último mes.\n")
        
        for ticker in tickers_list:
            # Extraemos el precio de cierre inicial y final del mes
            # yfinance devuelve estructuras distintas si es 1 o varios tickers, esto lo estandariza
            ticker_data = data[ticker] if len(tickers_list) > 1 else data
            
            start_price = ticker_data['Close'].iloc[0]
            end_price = ticker_data['Close'].iloc[-1]
            performance = ((end_price - start_price) / start_price) * 100
            
            insights.append(f"• {ticker}: Inicio ${start_price:.2f} -> Fin ${end_price:.2f} ({performance:+.2f}%)")
        
        # 4. Guardar los resultados reales
        task.llm_insight = "\n".join(insights)
        task.status = 'COMPLETED'
        task.save()
        
    except Exception as e:
        task.status = 'FAILED'
        task.llm_insight = f"Error conectando con el mercado: {str(e)}"
        task.save()