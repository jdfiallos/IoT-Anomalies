from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# 🔐 Autenticación por dispositivo: cada device_id tiene su token (API Key propia)
# Esto permite controlar individualmente qué dispositivo está autorizado
AUTHORIZED_DEVICES = {
    "device_normal_01": "Bearer token123",
    "device_anomal_99": "Bearer token456"
}

# 📁 Archivo CSV donde se guardan los datos de los dispositivos
CSV_FILE = "datos.csv"

# 📁 Configuración del sistema de logs de eventos (auditoría)
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "server.log")

# 🛡️ Si no existe el CSV, se crea con los encabezados necesarios
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["timestamp", "device_id", "temperature", "packets_sent", "alert"])
    df.to_csv(CSV_FILE, index=False)

# 🛡️ Se asegura que el directorio de logs exista
os.makedirs(LOG_DIR, exist_ok=True)

# 🧾 Función para guardar eventos en el log
# Esto es útil para detectar accesos no autorizados o anomalías en tiempo real
def log_event(event_type, device_id, extra=""):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {event_type} - {device_id} {extra}\n")

# 🔐 Valida que el dispositivo esté autorizado comparando su token con el esperado
def is_authorized(device_id, token):
    return AUTHORIZED_DEVICES.get(device_id) == token

# 🚪 Ruta que recibe los datos de los dispositivos IoT
@app.route('/data', methods=['POST'])
def receive_data():
    # 📥 Obtención del cuerpo JSON
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body"}), 400

    device_id = data.get("device_id")
    token = request.headers.get("Authorization")

    # 🔐 AUTENTICACIÓN: verifica que el device_id y su token coincidan
    # Si no, registra un intento de acceso no autorizado en los logs
    if not is_authorized(device_id, token):
        log_event("ACCESS_DENIED", device_id or "unknown")
        return jsonify({"error": "Unauthorized"}), 403

    # 🔎 Validación de que se envíen todos los campos necesarios
    required_fields = {"device_id", "temperature", "packets_sent"}
    if not required_fields.issubset(data.keys()):
        log_event("INVALID_PAYLOAD", device_id, str(data))
        return jsonify({"error": "Invalid payload"}), 400

    # ⚠️ Detecta si hay una temperatura anómala (> 80 °C) y lanza una alerta
    alert = "High temperature!" if data["temperature"] > 80 else ""

    # 📦 Fila que será guardada en el archivo CSV
    new_row = {
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": data["device_id"],
        "temperature": data["temperature"],
        "packets_sent": data["packets_sent"],
        "alert": alert
    }

    # 🛠️ Si el archivo CSV está vacío o da error, se inicializa correctamente
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception:
        df = pd.DataFrame(columns=["timestamp", "device_id", "temperature", "packets_sent", "alert"])

    # 📊 Agrega la nueva fila de datos al DataFrame y lo guarda
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    # 📘 Registra en los logs que se recibió correctamente un dato
    log_event("DATA_RECEIVED", device_id, f"Temp: {data['temperature']} Alert: {alert}")

    # ✅ Respuesta al cliente simulador
    return jsonify({"status": "success", "alert": alert}), 200

# 🚀 Inicia el servidor en modo debug (solo para desarrollo)
if __name__ == "__main__":
    app.run(debug=True)
