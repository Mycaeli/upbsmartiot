from flask import Flask, request, jsonify
from crate import client
from datetime import datetime
import uuid
import os

app = Flask(__name__)

# Connect to CrateDB
crate_host = os.getenv("CRATE_HOST", "db-crate")
connection = client.connect(f"http://{crate_host}:4200", username="crate")
cursor = connection.cursor()

@app.route('/endpoint', methods=['POST'])
def receive_data():
    data = request.json
    temperature = data.get("temperature")
    humidity = data.get("humidity")

    if temperature is not None and humidity is not None:
        # Generate a unique ID and timestamp for each entry
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()  # Using UTC for consistency across time zones

        # Insert data into CrateDB
        try:
            cursor.execute("""
                INSERT INTO sensor_data (id, temperature, humidity, timestamp) 
                VALUES (?, ?, ?, ?)
            """, (entry_id, temperature, humidity, timestamp))
            connection.commit()
            return jsonify({"status": "success", "id": entry_id}), 201
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

