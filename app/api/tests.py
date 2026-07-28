import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# The @pytest.mark.django_db decorator lets the test create a temporary database
# and destroy it when finished, so it doesn't pollute your real data.

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_portfolios():
    client = APIClient()
    # Try to access without a token
    response = client.get('/api/v1/portfolios/')
    
    # We expect the server to reject the request (HTTP 401)
    assert response.status_code == 401

@pytest.mark.django_db
def test_authenticated_user_sees_empty_list():
    # 1. Arrange
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = APIClient()
    client.force_authenticate(user=user) # Simulate a valid JWT
    
    # 2. Act
    response = client.get('/api/v1/portfolios/')
    
    # 3. Assert
    assert response.status_code == 200
    # Since this is a new user, the multi-tenant isolation should return []
    assert response.json() == []