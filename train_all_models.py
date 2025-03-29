import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib

def train_arima_model(csv_file: str, output_model: str):
    try:
        df = pd.read_csv(f"data/{csv_file}")
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        df.set_index('date', inplace=True)

        series = df['rate']
        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()

        joblib.dump(model_fit, f"models/{output_model}")
        print(f"✅ Modell gespeichert: models/{output_model}")

    except Exception as e:
        print(f"❌ Fehler bei {csv_file}: {e}")

if __name__ == "__main__":
    for file in os.listdir("data"):
        if file.startswith("chf_to_") and file.endswith(".csv"):
            currency = file.replace("chf_to_", "").replace(".csv", "").lower()
            train_arima_model(file, f"arima_{currency}.pkl")
