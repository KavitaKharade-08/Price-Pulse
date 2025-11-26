import os
import joblib
import pandas as pd
import numpy as np
from prophet import Prophet
from flask import Flask, request, jsonify
from flask_cors import CORS  # Optional: For allowing frontend requests

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (useful if connecting to React/Vue/etc.)

# Update this path if needed
MODELS_DIR = r"C:\Users\swaru\Downloads\avfs303_backend\avfs303_backend\saved_models"
CSV_FILE_PATH = r'D:\code\PricePulse\backend\dataset\commodity_dataset.csv'  

def get_demo_fallback_data(days=7):
    """Generates plausible dummy data if the model is broken"""
    print("⚠️ Model prediction failed (NaNs). Switching to Demo Fallback calculation.")
    dates = pd.date_range(start=pd.Timestamp.now(), periods=days)
    
    # Generate random prices around 35 range
    base_price = 35.0
    prices = [base_price + np.random.uniform(-2, 2) for _ in range(days)]
    
    df = pd.DataFrame({
        'ds': dates,
        'yhat': prices,
        'yhat_lower': [p - 1 for p in prices],
        'yhat_upper': [p + 1 for p in prices]
    })
    return df

def make_forecast(model, days=7):
    """Core logic to generate forecast from a loaded model"""
    # 1. CRITICAL FIX: Disable uncertainty sampling
    model.uncertainty_samples = 0

    # 2. Check if model is fitted
    if model.params is None or 'k' not in model.params or len(model.params['k']) == 0:
        return None

    # 3. Create future dataframe
    if model.history is not None and not model.history.empty:
        last_date = model.history['ds'].max()
    else:
        last_date = pd.Timestamp.now()
        
    future = pd.DataFrame({'ds': pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)})

    # 4. Fill regressors (Buffer Stock) ROBUSTLY
    if hasattr(model, 'extra_regressors') and model.extra_regressors:
        for reg in model.extra_regressors:
            avg_val = 5000.0 # Default fallback
            
            if hasattr(model, 'history') and reg in model.history:
                hist_mean = model.history[reg].mean()
                if not pd.isna(hist_mean):
                    avg_val = hist_mean
            
            future[reg] = float(avg_val)

    # 5. Predict
    try:
        forecast = model.predict(future)
        
        # Check for NaNs in result
        if forecast['yhat'].isna().any():
            return None
            
        # 6. Keep only relevant columns
        cols = ['ds', 'yhat']
        if 'yhat_lower' in forecast.columns: cols.append('yhat_lower')
        if 'yhat_upper' in forecast.columns: cols.append('yhat_upper')
        
        return forecast[cols]
        
    except Exception as e:
        print(f"⚠️ Prediction logic error: {e}")
        return None

@app.route("/api/commodities", methods=["GET"])
def get_commodities():
    try:
        # Check if file exists first to avoid crashing
        if not os.path.exists(CSV_FILE_PATH):
            return jsonify({"success": False, "error": "Data file not found"}), 404

        # 1. Read the CSV file
        df = pd.read_csv(CSV_FILE_PATH)

        # 2. Ensure numeric fields are numbers (Logic matching your original loop)
        # This converts errors (like empty strings) to NaN, then fills NaN with 0
        numeric_cols = ["min_price", "modal_price", "max_price"]
        
        for col in numeric_cols:
            if col in df.columns:
                # Force conversion to numeric, turn errors into NaN
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                # If the column is missing in CSV, create it with 0s
                df[col] = 0.0

        # 3. Convert DataFrame to a list of dictionaries
        data = df.to_dict(orient='records')

        return jsonify({"success": True, "data": data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """
    API Endpoint.
    Expected JSON Input:
    {
        "commodity": "Onion",
        "market": "Pune APMC",
        "days": 7
    }
    """
    try:
        data = request.get_json()
        
        # 1. Validate Input
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        commodity = data.get('commodity', '').strip().replace(" ", "_")
        market = data.get('market', '').strip().replace(" ", "_")
        days = int(data.get('days', 7))

        if not commodity or not market:
            return jsonify({"status": "error", "message": "Missing 'commodity' or 'market'"}), 400

        # 2. Load Model
        filename = f"{commodity}_{market}.pkl"
        filepath = os.path.join(MODELS_DIR, filename)

        if not os.path.exists(filepath):
            print(f"❌ Model not found: {filepath}")
            # Fallback for missing model
            forecast = get_demo_fallback_data(days)
            status = "fallback_missing_model"
        else:
            try:
                model = joblib.load(filepath)
                print(f"✅ Model loaded: {filename}")
                
                forecast = make_forecast(model, days)
                status = "success"

                if forecast is None:
                    forecast = get_demo_fallback_data(days)
                    status = "fallback_model_error"
                    
            except Exception as e:
                print(f"❌ Error loading/predicting: {e}")
                forecast = get_demo_fallback_data(days)
                status = "fallback_exception"

        # 3. Format Output for JSON
        # Convert Timestamp objects to string for JSON serialization
        forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%d')
        
        result = forecast.to_dict(orient='records')

        return jsonify({
            "status": status,
            "commodity": commodity,
            "market": market,
            "data": result
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Debug=True allows auto-reload on code changes
    app.run(debug=True, port=5001)