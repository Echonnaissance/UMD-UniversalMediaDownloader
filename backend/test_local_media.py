from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

resp = client.get('/api/local-media/list',
                  params={'path': 'C:/Users/Anthony Ferraro/Downloads'})
print('status:', resp.status_code)
print(resp.text)
