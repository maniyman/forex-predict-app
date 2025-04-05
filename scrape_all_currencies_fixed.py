import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from utils.db import db  # MongoDB-Verbindung

print("✅ Collections:", db.list_collection_names())

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CNY", "SEK", "NOK", "BRL", "INR"]

def scrape_fxtop_currency(target_currency: str, max_days: int = 10):
    base_currency = "CHF"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=max_days)

    url = (
        f"https://fxtop.com/en/historical-exchange-rates.php?"
        f"A=1&C1={base_currency}&C2={target_currency}"
        f"&DD1={start_date.day}&MM1={start_date.month}&YYYY1={start_date.year}"
        f"&DD2={end_date.day}&MM2={end_date.month}&YYYY2={end_date.year}"
        f"&FORMAT=HTML&LARGE=1&LANG=en"
    )

    print(f"\n🔍 Scraping {target_currency}: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        os.makedirs("html_debug", exist_ok=True)
        debug_path = f"html_debug/html_debug_{target_currency.lower()}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"border": "1"})
        if not table:
            print(f"❌ Keine Tabelle gefunden für {target_currency}")
            return

        rows = table.find_all("tr")
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                try:
                    date_str = cols[0].text.strip()
                    rate_str = cols[1].text.strip().replace(",", "")
                    date = datetime.strptime(date_str, "%A %d %B %Y")
                    rate = float(rate_str)

                    # Sicherstellen, dass nur Daten der letzten 10 Tage gespeichert werden
                    if start_date <= date <= end_date:
                        data.append({"date": date.strftime('%Y-%m-%d'), "rate": rate})  # Formatierung auf 'YYYY-MM-DD'

                        # 💾 MongoDB speichern
                        db.forex_rates.update_one(
                            {
                                "base": base_currency,
                                "target": target_currency,
                                "date": date.strftime("%Y-%m-%d")
                            },
                            {
                                "$set": {
                                    "value": rate
                                }
                            },
                            upsert=True
                        )

                except Exception:
                    continue

        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(by="date")

            os.makedirs("data", exist_ok=True)
            file_path = f"data/chf_to_{target_currency.lower()}.csv"
            df.to_csv(file_path, index=False)
            print(f"✅ Gespeichert: {file_path} ({len(df)} Werte)")
        else:
            print(f"⚠️ Keine gültigen Daten für {target_currency}")

        # Warten für 1 Sekunde, bevor die nächste Anfrage gestellt wird
        time.sleep(1)

    except Exception as e:
        print(f"💥 Fehler beim Scrapen von {target_currency}: {e}")


if __name__ == "__main__":
    for curr in CURRENCIES:
        scrape_fxtop_currency(curr)
