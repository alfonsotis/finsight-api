from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AnalysisTask, Portfolio
from .serializers import EmptySerializer, PortfolioSerializer
from .tasks import analyze_portfolio_task


class PortfolioViewSet(viewsets.ModelViewSet):
    # We removed the static queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]

    # 1. READ ISOLATION: Only returns the portfolios of the current user
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    # 2. WRITE ISOLATION: When creating a portfolio, assign the current user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 3. The analyze() method remains exactly as you had it
    @action(detail=True, methods=['post'], serializer_class=EmptySerializer)
    def analyze(self, request, pk=None):
        portfolio = self.get_object()
        analysis_task = AnalysisTask.objects.create(portfolio=portfolio)
        celery_task = analyze_portfolio_task.delay(analysis_task.id)
        analysis_task.celery_task_id = celery_task.id
        analysis_task.save()
        return Response({'message': 'Analysis started', 'task_id': analysis_task.id}, status=status.HTTP_202_ACCEPTED)