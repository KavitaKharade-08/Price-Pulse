# PricePulse — Stabilizing India's Food Basket 🚜 🇮🇳

**Theme:** Agriculture & Food Technology

---

## 🚀 Overview

PricePulse is an AI-driven **Decision Support System (DSS)** built for the Department of Consumer Affairs to move from a reactive to a proactive approach in managing price volatility for essential commodities. The system forecasts price volatility **15 days in advance** for 22 essential commodities (pulses, onions, etc.), and recommends strategic interventions.


**Video Walkthrough:** https://youtu.be/TfeYUZUoets

---

## 🚨 Problem

Price volatility creates uncertainty for both policymakers and farmers. Current monitoring relies on delayed reporting from 550 centers — by the time a spike is detected, the market often already reacts with panic selling, inflation, and inefficient use of buffer stocks.

**Consequences**

* Panic selling by farmers
* Consumer inflation
* Wasteful or untimely use of Government Buffer Stocks

---

## 💡 Solution

PricePulse aggregates real-time and historical data, applies ML forecasting, monitors volatility, and suggests context-aware actions (release, hold, divert) using a smart buffer-stock manager.

---

## 🌟 Key Features

* **Real-Time Monitoring Dashboard**

  * Live heatmap of India with price hotspots across 550 reporting centers.
  * Color-coded alerts (🔴 High Volatility, 🟡 Watch, 🟢 Stable).

* **AI Forecasting (The Prophet Engine)**

  * Uses Facebook Prophet and ARIMA to produce 15-day forecasts.
  * Handles trend, seasonality (festivals), and historical patterns.

* **Smart Buffer Stock Manager**

  * Dual-trigger logic based on **Price** and **Inventory Age**.
  * Recommends releases (High Price + Fresh Stock) and diversions (Stable Price + Expiring Stock).

* **Market Intelligence Radar (NLP)**

  * Scrapes headlines (e.g., "Truck Strike", "Rains in Nashik") and performs sentiment/scenario analysis to adjust forecasts.


---

## 🏗️ Architecture

graph LR
    %% Data Sources
    A[Field Officer] --> B(Data Aggregation)
    C[Historical Data] --> B

    %% AI Core
    B --> D{AI Engine (Prophet)}
    
    %% Decision Logic
    D -->|Forecast| E{Volatility Check}
    
    %% Outcomes
    E -- High Risk (>15%) --> F[🔴 Alert Dashboard]
    E -- Stable --> G[🟢 Standard View]
    
    %% Action
    F --> H[Buffer Stock Logic]

---

## ⚙️ Tech Stack

| Component  | Technology Used                           |
| ---------- | ----------------------------------------- |
| Frontend   | HTML5, Tailwind CSS, React.js, Leaflet.js |
| Backend    | Python (Flask)                            |
| ML Engine  | Facebook Prophet, ARIMA, Pandas, Joblib   |
| Database   | Firebase Realtime DB / JSON Store         |
| Deployment | Render (Backend), Netlify (Frontend)      |

---

## 📂 Project Structure

```
PricePulse/
├── app.py                 # Main Flask Application
├── requirements.txt       # Python Dependencies
├── price_model.pkl        # Pre-trained Prophet Model
├── static/                # CSS, Images, JS
│   ├── style.css
│   ├── i1.png             # Logo
│   ├── dashboard_preview.png
│   └── app_preview.png
├── templates/             # HTML Pages
│   ├── index.html         # Main Dashboard
│   ├── login.html         # Auth Portal
│   └── data-entry.html    # Field Officer App
└── data/
    └── commodity_prices.csv  # Historical Dataset
```

---

## 🛠️ Installation & Setup

**Prerequisites**

* Python 3.9+
* pip

**1. Clone the repository**

```bash
git clone https://github.com/YourUsername/PricePulse.git
cd PricePulse
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the application**

```bash
python app.py
```

Open the dashboard at: `http://127.0.0.1:5000/`

---

## 🔍 Usage & Developer Notes

* **Model file**: `price_model.pkl` — replace or re-train if you update Prophet/ARIMA hyperparameters.
* **Data ingestion**: Field officer inputs go to Firebase Realtime DB; backend pulls and aggregates into the forecasting pipeline.
* **Heatmap**: Leaflet.js reads recent prices from the backend endpoint (e.g., `/api/latest-prices`).
* **NLP scrapers**: Run cron jobs to fetch headlines and push sentiment adjustments to the ML engine.

---

## 📸 Screenshots

1. Landing Page- <img width="1886" height="877" alt="Screenshot 2025-11-25 183254" src="https://github.com/user-attachments/assets/2cb8e9e5-152e-4cb8-80b6-24a7eaf121c5" />

2. India HeatMap- ![WhatsApp Image 2025-11-25 at 19 15 38](https://github.com/user-attachments/assets/712729cb-8753-4e1a-b5d3-d157732feac6)
3. Dashboard - ![WhatsApp Image 2025-11-25 at 18 24 15 (2)](https://github.com/user-attachments/assets/dae9af96-9be0-45ee-92a9-1e55e0c7856d)
4. ![WhatsApp Image 2025-11-25 at 18 24 15](https://github.com/user-attachments/assets/bdcf2575-bfe7-484d-88d5-8680257ff884)





---

## 👥 Team — Tetragram

* **Swarup Chavan**
* **Satyam Mali**
* **Prashant Pawar**
* **Kavita Kharade**

Built with dedication and efforts.

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome.

---

## 📄 License

This project is open source- MIT License.

---

## 📫 Contact

For queries, reach out to: `kavitakharade22@gmail.com` or open an issue on GitHub.

---


