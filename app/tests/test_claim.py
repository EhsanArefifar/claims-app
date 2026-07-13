from fastapi.testclient import TestClient
from app.db import TestSessionDep, SessionDep
from app.main import app  # Import your FastAPI app instance

client = TestClient(app)  # Assuming 'app' is your FastAPI instance

def test_create_claim():
      
    app.dependency_overrides[SessionDep] = TestSessionDep  # Override the dependency for testing
    
    response = client.post(
        "/claims/",
        json={
            "claimant_name": "John Doe",
            "claim_amount": 1000.0,
            "claim_description": "Test claim"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claimant_name"] == "John Doe"
    assert data["claim_amount"] == 1000.0
    assert data["claim_description"] == "Test claim"
    assert data["status"] == "Submitted"
    assert "reference_number" in data

