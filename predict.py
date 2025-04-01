from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os
from datetime import datetime

# 🔌 MongoDB-Verbindung importieren
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

        csv_path = f"data/chf_to_{currency}.csv"
        model_path = f"models/arima_{currency}.pkl"

        if not os.path.exists(model_path) or not os.path.exists(csv_path):
            return jsonify({'error': 'Modell oder Daten fehlen.'}), 400

        df = pd.read_csv(csv_path)
        df = df.sort_values(by="date", ascending=False)

        model = joblib.load(model_path)
        prediction = model.forecast(steps=1)[0]

        if direction == "to_chf":
            prediction = 1 / prediction
            df["rate"] = 1 / df["rate"]

        prediction = round(prediction, 4)
        df_preview = df[["date", "rate"]].head(10).to_dict(orient="records")

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
