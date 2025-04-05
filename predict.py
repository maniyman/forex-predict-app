from flask import Flask, request, jsonify, render_template
import joblib
import os
from datetime import datetime
from utils.db import db

app = Flask(__name__)

# Plattformunabhängiger Pfad zur models/ Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_directory = os.path.join(BASE_DIR, "models")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    print(">>> RAW request.data:", request.data)
    print(">>> PARSED request.get_json():", request.get_json())

    try:
        data = request.get_json()
        print("Empfangene JSON-Daten:", data)

        currency = data.get('currency', '').lower()
        direction = data.get('direction', '').lower()  # "from_chf" oder "to_chf"

        if not currency or direction not in ["from_chf", "to_chf"]:
            return jsonify({'error': 'Ungültige Eingabedaten.'}), 400

        # Suche nach dem neuesten Modell basierend auf dem Erstellungsdatum im Dateinamen
        model_files = [f for f in os.listdir(model_directory) if f.startswith(f"arima_{currency}")]
        
        if not model_files:
            return jsonify({'error': 'Kein Modell für diese Währung gefunden.'}), 400

        # Sortiere die Modell-Dateien nach dem Datum im Dateinamen (z.B. "2025-04-05")
        model_files.sort(key=lambda x: datetime.strptime(x.split('_')[-1].replace('.pkl', ''), "%Y-%m-%d"), reverse=True)
        
        # Das neueste Modell wird jetzt das erste in der Liste sein
        latest_model_path = os.path.join(model_directory, model_files[0])

        model = joblib.load(latest_model_path)
        prediction = model.forecast(steps=1)[0]

        if direction == "to_chf":
            prediction = 1 / prediction  # Umrechnung von Fremdwährung ➔ CHF

        prediction = round(prediction, 4)

        # 🔎 Hole letzten 10 Kurse aus MongoDB
        query = {
            "base": "CHF" if direction == "from_chf" else currency.upper(),
            "target": currency.upper() if direction == "from_chf" else "CHF"
        }
        results = db.forex_rates.find(query).sort("date", -1).limit(21)

        df_preview = []
        for doc in results:
            try:
                rate = round(doc["value"], 4)
                if direction == "to_chf":
                    rate = round(1 / doc["value"], 4)  # Umrechnung von Fremdwährung ➔ CHF
                df_preview.append({
                    "date": datetime.strptime(doc["date"], "%Y-%m-%d").strftime("%d.%m.%Y"),
                    "rate": rate
                })
            except:
                continue

        # 💾 Vorhersage in MongoDB speichern
        db.forex_predictions.insert_one({
            "base": "CHF" if direction == "from_chf" else currency.upper(),
            "target": currency.upper() if direction == "from_chf" else "CHF",
            "date": datetime.today().strftime("%Y-%m-%d"),
            "predicted_value": prediction,
            "model": "ARIMA"
        })

        return jsonify({
            "prediction": prediction,
            "history": df_preview,
            "direction": direction  # Füge die Richtung zur Antwort hinzu
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
