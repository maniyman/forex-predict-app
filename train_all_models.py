import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib
from datetime import datetime, timedelta
from utils.db import db  # MongoDB-Verbindung

def train_arima_model(currency: str, output_model: str, max_days: int = 10):
    try:
        # Berechne das Start- und Enddatum für die letzten max_days Tage
        end_date = datetime.today()
        start_date = end_date - timedelta(days=max_days)

        # Abrufen der Daten aus MongoDB für die letzten max_days
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
        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()

        # Modell speichern
        joblib.dump(model_fit, f"models/{output_model}")
        print(f"✅ Modell gespeichert: models/{output_model}")

    except Exception as e:
        print(f"❌ Fehler beim Trainieren des Modells für {currency}: {e}")

if __name__ == "__main__":
    # Liste der Währungen aus der MongoDB abfragen
    currencies = db.forex_rates.distinct("target")
    
    for currency in currencies:
        # Sicherstellen, dass nur Währungen trainiert werden, die für CHF existieren
        if currency != "CHF":
            train_arima_model(currency, f"arima_{currency.lower()}.pkl")
