PricePulse - Stabilizing India's Food Basket 🚜 🇮🇳

Theme: Agriculture & Food Technology

📌 Overview

PricePulse is an AI-driven Decision Support System (DSS) designed for the Department of Consumer Affairs. It transitions the government's approach from Reactive to Proactive by predicting price volatility in 22 essential commodities (Pulses, Onions, etc.) 15 days in advance.

🔗 Live Demo: [Insert Your Netlify/Render Link Here]

📹 Video Walkthrough: [Insert YouTube Link Here (Optional)]

🚨 The Problem

Price volatility creates uncertainty for policymakers and farmers.

Current Method: Relies on delayed reporting from 550 centers. By the time a spike is detected, the market is already disrupted.

The Consequence: Panic selling by farmers, inflation for consumers, and inefficient use of Buffer Stocks by the government.

💡 The Solution

PricePulse aggregates real-time data, forecasts trends using ML, and suggests strategic interventions.

🌟 Key Features

Real-Time Monitoring Dashboard:

Live Heatmap of India showing price hotspots across 550 Reporting Centers.

Color-coded alerts (Red = High Volatility).

AI Forecasting (The Prophet Engine):

Uses Facebook Prophet & ARIMA models to forecast prices for the next 15 days.

Handles seasonality (festivals), trends, and historical patterns.

Smart Buffer Stock Manager:

Dual-Trigger Logic: Recommends action based on Price AND Inventory Age.

High Price + Fresh Stock → Release to Market (Cool down prices).

Stable Price + Expiring Stock → Divert to Welfare Schemes/PDS (Prevent wastage).

Market Intelligence Radar (NLP):

Scrapes news headlines (e.g., "Truck Strike", "Rains in Nasik") to adjust forecasts based on sentiment analysis.

Lok Bhasha (Multilingual Support):

One-click translation to 10+ Indian languages (Hindi, Marathi, Tamil, etc.) for local accessibility.

Geo-Fenced Data Entry:

Prevents fraud by allowing Field Officers to submit data only when physically present at the Mandi (GPS Verified).

🏗️ Tech Stack

Component

Technology Used

Frontend

HTML5, Tailwind CSS, React.js (Embedded), Leaflet.js (Maps)

Backend

Python (Flask)

ML Engine

Facebook Prophet, ARIMA, Pandas, Joblib

Database

Firebase Realtime DB / JSON Store

Deployment

Render (Backend), Netlify (Frontend)

⚙️ Architecture

graph LR
    A[Field Officer] -->|Geo-Fenced Input| B(Data Aggregation)
    C[Historical Data] --> B
    B --> D{AI Engine (Prophet)}
    D -->|Forecast| E[Volatility Check]
    E -- High Risk --> F[🔴 Alert Dashboard]
    E -- Stable --> G[🟢 Standard View]
    F --> H[Buffer Stock Logic]


🚀 Installation & Setup

Follow these steps to run the project locally:

Prerequisites

Python 3.9+

Pip

1. Clone the Repository

git clone
cd PricePulse-SIH


2. Install Dependencies

pip install -r requirements.txt


3. Run the Application

python app.py


The dashboard will launch at http://127.0.0.1:5000/

📂 Project Structure

PricePulse/
├── app.py                 # Main Flask Application
├── requirements.txt       # Python Dependencies
├── price_model.pkl        # Pre-trained Prophet Model
├── static/                # CSS, Images, JS
│   ├── style.css
│   └── js/
├── templates/             # HTML Pages
│   ├── index.html         # Main Dashboard
│   ├── login.html         # Auth Portal
│   └── data-entry.html    # Field Officer App
└── data/
    └── commodity_prices.csv  # Historical Dataset


📸 Screenshots

1. Policymaker Dashboard (War Room)

Real-time Heatmap and Price Forecasts

2. Geo-Verified Field App

GPS-Locked Data Entry Form

👥 Team Tetragram

Swarup Chavan

Satyam Mali

Prashant Pawar

Kavita Kharade

Built with dedication and efforts.
