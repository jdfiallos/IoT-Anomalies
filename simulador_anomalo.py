import requests
import time
import random

API_KEY = "token456"
URL = "http://127.0.0.1:5000/data"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

for i in range(10):
    payload = {
        "device_id": "device_anomal_99",
        "temperature": round(random.uniform(85.0, 95.0), 2),
        "packets_sent": random.randint(500, 1000)
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    print("Anómalo:", response.json())
    time.sleep(1)
