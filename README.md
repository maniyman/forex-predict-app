# CHF Wechselkurs-Prognose

Dieses Projekt ist Teil des Moduls "MDM" im Studiengang Wirtschaftsinformatik. Es umfasst das Scrapen, Trainieren und Bereitstellen eines Machine-Learning-Modells zur Vorhersage von Wechselkursen zwischen dem Schweizer Franken (CHF) und 11 ausgewählten Währungen. Die Anwendung nutzt moderne Technologien wie Flask, ARIMA-Zeitreihenmodelle und bietet ein ansprechendes Frontend mit Chart-Darstellung.

---

## 📆 Projektziele
- Eigener HTML-Scraper für Wechselkurse (keine API!)
- Vorhersage von CHF-Wechselkursen per Zeitreihenmodell
- Interaktive Web-App mit Dropdown, Diagramm und Verlauf
- Deployment auf Azure (optional)
- Dokumentation + Screencast zur Erklärung

---

## 🚀 Technologien
- **Python** 3.10+
- **Flask** (Webserver & API)
- **pandas**, **statsmodels** (ARIMA-Modell)
- **BeautifulSoup** (Scraping)
- **Chart.js** (Frontend-Diagramm)
- **HTML / CSS / JS** (responsive UI)

---

## 📂 Projektstruktur

```
forex_prediction/
├── main.py                   # Flask-Server starten
├── predict.py               # Routen-Logik & Vorhersage
├── train_all_models.py      # ARIMA-Modelle trainieren
├── scrape_all_currencies.py # Wechselkurse scrapen
├── /data/                   # CSV-Dateien mit Kursdaten
├── /models/                 # ARIMA-Modelle (.pkl)
├── /templates/index.html    # UI-Layout
├── /static/style.css        # Styling & Animationen
├── requirements.txt         # Alle Python-Abhängigkeiten
└── README.md                # Projektbeschreibung (dieses Dokument)
```

---

## ⚖️ Währungen
- USD, EUR, GBP, JPY, CAD, AUD, CNY, SEK, NOK, BRL, INR
- Beide Richtungen auswählbar: CHF → Währung oder Währung → CHF

---

## ⚡ Funktionen
- Scraping von **fxtop.com** (reines HTML, kein API)
- ARIMA-Zeitreihenmodell pro Währung
- Dropdown-Auswahl + Richtung (mit Invertierung)
- Prognoseanzeige + Chart.js-Verlaufsgrafik
- Tabelle der letzten 10 Tageskurse
- Sauberes UI mit Animation & Responsiveness

---

## 🚫 Noch nicht umgesetzt (optional):
- [ ] GitHub Actions für automatisiertes Training & Scraping


---

## 🔧 Setup & Ausführen

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. Scraping starten (90 Tage Daten pro Währung)
python scrape_all_currencies.py

# 3. Modelle trainieren
python train_all_models.py

# 4. Webserver starten
python main.py
```

Dann im Browser öffnen: [http://localhost:5000](http://localhost:5000)

---

## 🎥 Screencast-Inhalte (Checkliste)
- [ ] Scraper & CSV zeigen
- [ ] Trainingscode erklären
- [ ] UI & Chart demonstrieren
- [ ] Vorhersage mit Wechsel-Richtung zeigen
- [ ] (optional) Azure-Demo

---

## 📄 Autor / Projekt
Dieses Projekt wurde im Rahmen von **MDM Projekt 1** eigenständig umgesetzt und dient als Anwendungsbeispiel für Scraping, Modellierung und Deployment mit Python & Flask.

---

## 🔄 Automatisierung & Deployment

Das Projekt nutzt einen GitHub Actions Workflow, um täglich neue Wechselkursdaten zu scrapen, Modelle neu zu trainieren und ein aktualisiertes Docker-Image zu erstellen.

### 🧭 Workflow-Ablauf:
- Läuft täglich um 06:00 UTC (08:00 MEZ)
- Scraping der Wechselkurse mit `scrape_all_currencies_fixed.py`
- Modelltraining mit `train_all_models.py`
- Erstellung eines Docker-Images
- Push des Images zu Azure Container Registry (ACR)

```bash
forexacr144.azurecr.io/forex-app:latest
```

### ⚠️ Hinweis:
Das Deployment zur Azure Web App erfolgt aktuell **nicht automatisch**, sondern wird manuell ausgelöst (z. B. über `az webapp restart`). Die Integration per Publish Profile ist vorbereitet, aber derzeit deaktiviert.

