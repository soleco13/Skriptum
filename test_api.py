import requests
import json

# Тест API для BPMN Access
url = "http://localhost:8000/api/bpmn-access/"
headers = {
    "Authorization": "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU4Mjk2NzU5LCJpYXQiOjE3NTgyMTAzNTksImp0aSI6IjY4MzU4YWY0NGZjZjQ5ZTI5OGE0NTJjMjgxNDJiOTUzIiwidXNlcl9pZCI6Nn0.mGA0fVM7SUdyH1--FpW894cDrZzHq5Cm0KBy_xj6SXs",
    "Content-Type": "application/json"
}

# Тест GET запроса
print("GET запрос:")
response = requests.get(url, headers=headers)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")

# Тест POST запроса
print("\nPOST запрос:")
data = {
    "diagram": 21,
    "user": 1,
    "access_level": "view"
}
response = requests.post(url, headers=headers, json=data)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")
