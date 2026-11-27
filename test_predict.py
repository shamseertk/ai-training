
from fastapi.testclient import TestClient
from ai_fastapi import app

client = TestClient(app)

def test_predict_good():
    response = client.post("/predict", json={"text": "This is a great product!"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "positive"
    assert 0 <= data["score"] <= 1

def test_predict_bad():
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422

def test_predict_edge():
    response = client.post("/predict", json={"text": "This is a terrible product!"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "negative"
    assert 0 <= data["score"] <= 1

