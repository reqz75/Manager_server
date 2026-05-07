import requests

url = "http://localhost:8000/load_reports"
headers = {
    "Content-Type": "application/json",
    "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dpbiI6InNpZG9yb3ZfcyIsImV4cCI6MTc3ODAxMDc1OX0.gTx0wVyvXNhTsPd2OOVeiD6USD0QT6qKgK9KXYvvfS4"
}
data = {
    "task_id": 4
}

response = requests.post(url, json=data, headers=headers)
print(response.status_code)
print(response.json())