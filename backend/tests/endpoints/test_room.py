from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
