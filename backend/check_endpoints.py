from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

root = client.get("/")
health = client.get("/api/health")

print("GET / ->", root.status_code)
print(root.text[:300])
print()
print("GET /api/health ->", health.status_code)
try:
    print(health.json())
except Exception as e:
    print("(json decode error)", e)
