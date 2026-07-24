from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated # <--- Importar esto
from .models import Portfolio, AnalysisTask
from .serializers import PortfolioSerializer
from .tasks import analyze_portfolio_task

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated] # <--- ¡El cerrojo activado!


    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        portfolio = self.get_object()
        
        # 1. Crear el registro de la tarea en la DB
        analysis_task = AnalysisTask.objects.create(portfolio=portfolio)
        
        # 2. Enviar el trabajo a Redis/Celery de forma asíncrona
        celery_task = analyze_portfolio_task.delay(analysis_task.id)
        
        # 3. Guardar el ID interno de Celery (útil para monitoreo futuro)
        analysis_task.celery_task_id = celery_task.id
        analysis_task.save()
        
        return Response({
            'message': 'Analysis started successfully', 
            'task_id': analysis_task.id
        }, status=status.HTTP_202_ACCEPTED)