import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestOrganizationEndpoints:
    """Test suite for organization endpoints"""
    
    def test_create_organization_success(self):
        """Test successful organization creation"""
        payload = {
            "organization_name": "test_company",
            "email": "admin@test.com",
            "password": "TestPass123"
        }
        
        response = client.post("/org/create", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["organization_name"] == "test_company"
        assert data["admin_email"] == "admin@test.com"
        assert "collection_name" in data
        assert data["collection_name"].startswith("org_")
    
    def test_create_organization_duplicate(self):
        """Test creating duplicate organization"""
        payload = {
            "organization_name": "duplicate_org",
            "email": "admin@duplicate.com",
            "password": "TestPass123"
        }
        
        # Create first time
        response1 = client.post("/org/create", json=payload)
        assert response1.status_code == 201
        
        # Try to create again
        response2 = client.post("/org/create", json=payload)
        assert response2.status_code == 400
    
    def test_create_organization_invalid_name(self):
        """Test creating organization with invalid name"""
        payload = {
            "organization_name": "invalid name!",  # Contains space and special char
            "email": "admin@test.com",
            "password": "TestPass123"
        }
        
        response = client.post("/org/create", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_organization_weak_password(self):
        """Test creating organization with weak password"""
        payload = {
            "organization_name": "test_weak_pwd",
            "email": "admin@test.com",
            "password": "weak"  # Too short, no uppercase, no digit
        }
        
        response = client.post("/org/create", json=payload)
        assert response.status_code == 422
    
    def test_get_organization_success(self):
        """Test getting organization by name"""
        # First create an organization
        create_payload = {
            "organization_name": "get_test_org",
            "email": "admin@gettest.com",
            "password": "TestPass123"
        }
        client.post("/org/create", json=create_payload)
        
        # Now get it
        response = client.get("/org/get?organization_name=get_test_org")
        
        assert response.status_code == 200
        data = response.json()
        assert data["organization_name"] == "get_test_org"
        assert data["admin_email"] == "admin@gettest.com"
    
    def test_get_organization_not_found(self):
        """Test getting non-existent organization"""
        response = client.get("/org/get?organization_name=nonexistent_org")
        assert response.status_code == 404
    
    def test_update_organization_unauthorized(self):
        """Test updating organization without authentication"""
        payload = {
            "organization_name": "updated_org",
            "email": "admin@test.com",
            "password": "TestPass123"
        }
        
        response = client.put("/org/update", json=payload)
        assert response.status_code == 403  # Forbidden - no auth
    
    def test_delete_organization_unauthorized(self):
        """Test deleting organization without authentication"""
        response = client.delete("/org/delete?organization_name=test_org")
        assert response.status_code == 403  # Forbidden - no auth


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup test data after each test"""
    yield
