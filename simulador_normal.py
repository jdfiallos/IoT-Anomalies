import requests
import time
import random

API_KEY = "SECRET123"
URL = "http://127.0.0.1:5000/data"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

for i in range(10):
    payload = {
        "device_id": "device_normal_01",
        "temperature": round(random.uniform(22.0, 28.0), 2),
        "packets_sent": random.randint(50, 100)
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    print("Normal:", response.json())
    time.sleep(1)
