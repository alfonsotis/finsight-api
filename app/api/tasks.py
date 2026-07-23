import time
from celery import shared_task
from .models import AnalysisTask

@shared_task
def analyze_portfolio_task(db_task_id):
    try:
        # 1. Recuperamos la tarea de la base de datos
        task = AnalysisTask.objects.get(id=db_task_id)
        task.status = 'PROCESSING'
        task.save()
        
        # 2. Aquí irán las llamadas a Yahoo Finance y OpenAI
        # Simulamos el tiempo de procesamiento...
        time.sleep(5) 
        
        # 3. Guardamos el resultado
        task.llm_insight = f"Análisis simulado completado para {task.portfolio.name}. Volatilidad controlada."
        task.status = 'COMPLETED'
        task.save()
        
    except Exception as e:
        task.status = 'FAILED'
        task.llm_insight = str(e)
        task.save()