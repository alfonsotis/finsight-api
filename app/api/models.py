# Disable pyright missing-module-source reporting for environments without installed Django
# pyright: reportMissingModuleSource=false
import uuid

from django.contrib.auth.models import User
from django.db import models


class Portfolio(models.Model):
    """
    Represents a set of financial assets (e.g. SPY, AAPL, NVDA)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    tickers = models.JSONField(help_text="Lista de tickers, ej: ['AAPL', 'MSFT']")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AnalysisTask(models.Model):
    """
    Tracks the asynchronous Celery processing state and stores the LLM result.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='analyses')
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    llm_insight = models.TextField(blank=True, null=True, help_text="El análisis generado por la IA")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.portfolio.name} - {self.status}"