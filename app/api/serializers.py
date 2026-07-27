from rest_framework import serializers

from .models import AnalysisTask, Portfolio


class AnalysisTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisTask
        fields = ['id', 'status', 'llm_insight', 'created_at']

class PortfolioSerializer(serializers.ModelSerializer):
    analyses = AnalysisTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'tickers', 'analyses', 'created_at']