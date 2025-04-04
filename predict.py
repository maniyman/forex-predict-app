from flask import Flask, request, jsonify, render_template
import joblib
import os
from datetime import datetime
from utils.db import db

app = Flask(__name__)

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

        model_path = f"models/arima_{currency}.pkl"

        if not os.path.exists(model_path):
            return jsonify({'error': 'Modell fehlt.'}), 400

        model = joblib.load(model_path)
        prediction = model.forecast(steps=1)[0]

        if direction == "to_chf":
            prediction = 1 / prediction

        prediction = round(prediction, 4)

        # 🔎 Hole letzten 10 Kurse aus MongoDB
        query = {
            "base": "CHF" if direction == "from_chf" else currency.upper(),
            "target": currency.upper() if direction == "from_chf" else "CHF"
        }
        results = db.forex_rates.find(query).sort("date", -1).limit(10)

        df_preview = []
        for doc in results:
            try:
                rate = round(doc["value"], 4)
                if direction == "to_chf":
                    rate = round(1 / doc["value"], 4)
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
            "history": df_preview
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

