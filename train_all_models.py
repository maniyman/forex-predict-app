import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib
from datetime import datetime, timedelta
from utils.db import db  # MongoDB-Verbindung

def train_arima_model(currency: str, output_model: str, max_days: int = 20):
    try:
        # Berechne das heutige Datum
        end_date = datetime.today()

        # Abrufen des neuesten Datums aus den Daten für die angegebene Währung
        latest_data = db.forex_rates.find(
            {"base": "CHF", "target": currency.upper()},
            sort=[("date", -1)], limit=1
        )

        latest_date = None
        for doc in latest_data:
            latest_date = doc["date"]

        if not latest_date:
            print(f"⚠️ Keine Daten für {currency} in der Datenbank.")
            return

        # Berechne das Startdatum, indem die letzten max_days Tage ab dem neuesten Datum genommen werden
        start_date = datetime.strptime(latest_date, "%Y-%m-%d") - timedelta(days=max_days)

        # Abrufen der Daten aus MongoDB für die letzten max_days Tage, basierend auf dem neuesten Datum
        data = db.forex_rates.find(
            {
                "base": "CHF",
                "target": currency.upper(),
                "date": {"$gte": start_date.strftime("%Y-%m-%d")}
            }
        )

        # Umwandeln der Daten in ein DataFrame
        df = pd.DataFrame(list(data))
        
        if df.empty:
            print(f"⚠️ Keine Daten für {currency} in den letzten {max_days} Tagen.")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        df.set_index('date', inplace=True)

        # Zeitreihe der Wechselkurse
        series = df['value']  # 'value' ist der Wechselkurs, der gespeichert wurde
        
        # ARIMA-Modell trainieren
        model = ARIMA(series, order=(1, 1, 1))  # Beispiel: ARIMA(1,1,1), kannst du nach Bedarf anpassen
        model_fit = model.fit()

        # Heutiges Datum für den Modellnamen hinzufügen
        creation_date = datetime.today().strftime("%Y-%m-%d")
        model_name = f"arima_{currency.lower()}_{creation_date}.pkl"

        # Modell speichern
        joblib.dump(model_fit, f"models/{model_name}")
        print(f"✅ Modell gespeichert: models/{model_name}")

    except Exception as e:
        print(f"❌ Fehler beim Trainieren des Modells für {currency}: {e}")

if __name__ == "__main__":
    # Liste der Währungen aus der MongoDB abfragen
    currencies = db.forex_rates.distinct("target")
    
    for currency in currencies:
        # Sicherstellen, dass nur Währungen trainiert werden, die für CHF existieren
        if currency != "CHF":
            train_arima_model(currency, f"arima_{currency.lower()}.pkl", max_days=20)  # Erhöht auf 20 Tage
