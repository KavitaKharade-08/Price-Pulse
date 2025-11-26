from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.auth_routes import auth_routes
from firebase_config import db
import random
import pandas as pd

app = Flask(__name__)
CORS(app)

# Register Auth Blueprint
app.register_blueprint(auth_routes, url_prefix='/pricepulse')

# Commodities API
@app.route("/api/commodities", methods=["GET"])
def get_commodities():
    try:
        collection_ref = db.collection("commodities")
        docs = collection_ref.stream()
        data = []
        for doc in docs:
            item = doc.to_dict()
            for key in ["min_price", "modal_price", "max_price"]:
                item[key] = float(item.get(key, 0))
            data.append(item)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Sentiment API
@app.route("/api/market_sentiment", methods=["GET"])
def market_sentiment():
    sample_news = [
        {"headline": "Heavy rainfall disrupts onion supply in Nashik region", "sentiment": "negative", "score": -0.72, "impact": "+8%"},
        {"headline": "Transport strike called in Maharashtra APMCs", "sentiment": "negative", "score": -0.63, "impact": "+5%"},
        {"headline": "Improved crop yield expected for Tur Dal in Gujarat", "sentiment": "positive", "score": 0.41, "impact": "-3%"}
    ]
    item = random.choice(sample_news)
    return jsonify({"success": True, "headline": item["headline"], "sentiment": item["sentiment"], "score": item["score"], "impact": item["impact"]})

# ML Forecast API
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        commodity = data["commodity"]
        market = data["market"]
        days = int(data["days"])
        forecast_result = run_forecast(commodity, market, days)
        return jsonify({"success": True, "forecast": forecast_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
