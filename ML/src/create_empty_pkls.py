import os
import pandas as pd
from prophet import Prophet
import joblib

# Path to saved_models
MODELS_DIR = r"D:\avfs303_backend\saved_models"
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# List of commodities
commodities = [
    "Onion", "Tomato", "Potato", "Garlic", "Ginger", "GreenChili",
    "Carrot", "Cabbage", "Cauliflower", "Brinjal", "Apple", "Banana",
    "Grapes", "Mango", "Wheat", "Rice", "Gram", "TurDal", "UradDal",
    "MasurDal", "Sugar", "Soybean"
]

# Create dummy data and models
for comm in commodities:
    # Create dummy dataframe with 30 days
    df = pd.DataFrame({
        'ds': pd.date_range(start='2025-01-01', periods=30, freq='D'),
        'y': [100 + i for i in range(30)],  # dummy price trend
        'buffer_stock_qty_kg': [5000]*30
    })

    model = Prophet(daily_seasonality=True)
    model.add_regressor('buffer_stock_qty_kg')
    model.fit(df)

    # Save model
    filename = os.path.join(MODELS_DIR, f"{comm}.pkl")
    joblib.dump(model, filename)
    print(f" Dummy model saved: {filename}")

print("All dummy models created successfully.")
