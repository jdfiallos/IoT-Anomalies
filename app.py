from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
API_KEY = "SECRET123"  # en producción, usar variables de entorno

CSV_FILE = "datos.csv"
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["timestamp", "device_id", "temperature", "packets_sent", "alert"])
    df.to_csv(CSV_FILE, index=False)

@app.route('/data', methods=['POST'])
def receive_data():
    # Autenticación básica por API Key
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {API_KEY}":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    # Validación básica
    required_fields = {"device_id", "temperature", "packets_sent"}
    if not data or not required_fields.issubset(data.keys()):
        return jsonify({"error": "Invalid payload"}), 400

    # Generar alerta si temperatura anómala (> 80°C)
    alert = "High temperature!" if data["temperature"] > 80 else ""

    new_row = {
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": data["device_id"],
        "temperature": data["temperature"],
        "packets_sent": data["packets_sent"],
        "alert": alert
    }

    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    return jsonify({"status": "success", "alert": alert}), 200

if __name__ == "__main__":
    app.run(debug=True)
