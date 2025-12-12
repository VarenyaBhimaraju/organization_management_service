import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthenticationEndpoints:
    """Test suite for authentication endpoints"""
    
    @pytest.fixture
    def created_org(self):
        """Fixture to create an organization for testing"""
        payload = {
            "organization_name": "auth_test_org",
            "email": "admin@authtest.com",
            "password": "AuthTest123"
        }
        response = client.post("/org/create", json=payload)
        assert response.status_code == 201
        return response.json()
    
    def test_admin_login_success(self, created_org):
        """Test successful admin login"""
        login_payload = {
            "email": "admin@authtest.com",
            "password": "AuthTest123"
        }
        
        response = client.post("/admin/login", json=login_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0
    
    def test_admin_login_wrong_password(self, created_org):
        """Test login with wrong password"""
        login_payload = {
            "email": "admin@authtest.com",
            "password": "WrongPassword123"
        }
        
        response = client.post("/admin/login", json=login_payload)
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_admin_login_nonexistent_email(self):
        """Test login with non-existent email"""
        login_payload = {
            "email": "nonexistent@test.com",
            "password": "TestPass123"
        }
        
        response = client.post("/admin/login", json=login_payload)
        assert response.status_code == 401
    
    def test_get_current_admin_with_valid_token(self, created_org):
        """Test getting current admin info with valid token"""
        # First login
        login_payload = {
            "email": "admin@authtest.com",
            "password": "AuthTest123"
        }
        login_response = client.post("/admin/login", json=login_payload)
        token = login_response.json()["access_token"]
        
        # Get current admin info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/admin/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@authtest.com"
        assert "admin_id" in data
        assert "organization_id" in data
    
    def test_get_current_admin_without_token(self):
        """Test getting current admin info without token"""
        response = client.get("/admin/me")
        assert response.status_code == 403  # Forbidden
    
    def test_get_current_admin_with_invalid_token(self):
        """Test getting current admin info with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/admin/me", headers=headers)
        assert response.status_code == 401  # Unauthorized
    
    def test_token_contains_correct_claims(self, created_org):
        """Test that JWT token contains correct claims"""
        # Login
        login_payload = {
            "email": "admin@authtest.com",
            "password": "AuthTest123"
        }
        login_response = client.post("/admin/login", json=login_payload)
        token = login_response.json()["access_token"]
        
        # Decode token by calling /admin/me
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/admin/me", headers=headers)
        
        assert me_response.status_code == 200
        data = me_response.json()
        
        # Verify claims
        assert "admin_id" in data
        assert "email" in data
        assert "organization_id" in data
        assert data["email"] == "admin@authtest.com"


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup test data after each test"""
    yield
   
