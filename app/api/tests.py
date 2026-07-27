import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# El decorador @pytest.mark.django_db le permite al test crear una base de datos 
# de prueba vacía y destruirla al terminar, para no ensuciar tus datos reales.

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_portfolios():
    client = APIClient()
    # Intentamos entrar sin Token
    response = client.get('/api/v1/portfolios/')
    
    # Esperamos que el servidor nos dé un portazo (HTTP 401)
    assert response.status_code == 401

@pytest.mark.django_db
def test_authenticated_user_sees_empty_list():
    # 1. Arrange (Preparar)
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.force_authenticate(user=user) # Simulamos que tiene un JWT válido
    
    # 2. Act (Actuar)
    response = client.get('/api/v1/portfolios/')
    
    # 3. Assert (Comprobar)
    assert response.status_code == 200
    # Como es un usuario nuevo, el aislamiento Multi-tenant debe devolver []
    assert response.json() == []