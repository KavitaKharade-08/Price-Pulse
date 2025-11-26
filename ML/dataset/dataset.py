import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# --- CONFIGURATION ---
TARGET_ROWS = 14000
OUTPUT_FILE = "dataset/commodity_dataset.csv"

# --- 1. DEFINE COMMODITIES (NO FRUITS) ---
# Base Price is the average price in ₹/kg
COMMODITIES = {
    "Onion":       {"base": 35, "variety": "Red/Nashik", "cat": "Veg"},
    "Tomato":      {"base": 40, "variety": "Hybrid", "cat": "Veg"},
    "Potato":      {"base": 25, "variety": "Desi/Local", "cat": "Veg"},
    "Garlic":      {"base": 120, "variety": "Desi", "cat": "Veg"},
    "Ginger":      {"base": 90, "variety": "Local", "cat": "Veg"},
    "Green Chilli":{"base": 60, "variety": "Teja", "cat": "Veg"},
    "Rice":        {"base": 45, "variety": "Basmati/Common", "cat": "Cereal"},
    "Wheat":       {"base": 30, "variety": "Sharbati", "cat": "Cereal"},
    "Atta":        {"base": 35, "variety": "Whole Wheat", "cat": "Cereal"},
    "Tur Dal":     {"base": 110, "variety": "Unpolished", "cat": "Pulse"},
    "Gram Dal":    {"base": 75, "variety": "Desi", "cat": "Pulse"},
    "Moong Dal":   {"base": 95, "variety": "Split", "cat": "Pulse"},
    "Urad Dal":    {"base": 105, "variety": "Black", "cat": "Pulse"},
    "Masoor Dal":  {"base": 85, "variety": "Red", "cat": "Pulse"},
    "Mustard Oil": {"base": 140, "variety": "Kachi Ghani", "cat": "Oil"},
    "Groundnut Oil":{"base": 180, "variety": "Filtered", "cat": "Oil"},
    "Soya Oil":    {"base": 125, "variety": "Refined", "cat": "Oil"},
    "Sunflower Oil":{"base": 130, "variety": "Refined", "cat": "Oil"},
    "Palm Oil":    {"base": 95, "variety": "Imported", "cat": "Oil"},
    "Sugar":       {"base": 42, "variety": "M-30", "cat": "Essential"},
    "Milk":        {"base": 55, "variety": "Toned", "cat": "Essential"},
    "Salt":        {"base": 20, "variety": "Iodized", "cat": "Essential"}
}

# --- 2. DEFINE MARKETS (Real APMC Markets) ---
MARKETS = [
    {"state": "Maharashtra", "district": "Mumbai", "market": "Vashi APMC"},
    {"state": "Delhi", "district": "Delhi", "market": "Azadpur APMC"},
    {"state": "Karnataka", "district": "Bengaluru", "market": "Yeshwantpur APMC"},
    {"state": "Uttar Pradesh", "district": "Lucknow", "market": "Dubagga Mandi"}
]

def generate_data():
    if not os.path.exists("dataset"):
        os.makedirs("dataset")

    data = []
    end_date = datetime.now()
    # We go back ~1.5 years to ensure we cross 14,000 rows with good history
    days_to_generate = 400 
    start_date = end_date - timedelta(days=days_to_generate)
    
    print(f"🚀 Generating dataset for {len(COMMODITIES)} commodities across {len(MARKETS)} markets...")

    for day in range(days_to_generate):
        curr_date = start_date + timedelta(days=day)
        date_str = curr_date.strftime("%Y-%m-%d")
        
        # Seasonality Factor (Sine wave to simulate yearly price trends)
        day_of_year = curr_date.timetuple().tm_yday
        season_factor = np.sin(2 * np.pi * day_of_year / 365)

        for mkt in MARKETS:
            for name, details in COMMODITIES.items():
                
                # 1. Base Price Calculation
                base = details["base"]
                
                # 2. Add Seasonality (Onion/Tomato fluctuate more)
                if name in ["Onion", "Tomato", "Potato"]:
                    variation = season_factor * (base * 0.3) # 30% variation
                else:
                    variation = season_factor * (base * 0.1) # 10% variation (stable crops)
                
                # 3. Add Inflation (Prices go up slightly over time)
                inflation = (day / 365) * (base * 0.05)
                
                # 4. Random Daily Noise (Supply/Demand shocks)
                noise = np.random.normal(0, base * 0.05)
                
                # Calculate Modal Price
                modal_price = base + variation + inflation + noise
                modal_price = max(details["base"] * 0.5, modal_price) # Can't drop too low
                modal_price = round(modal_price, 2)
                
                # Min and Max Prices relative to Modal
                min_price = round(modal_price * random.uniform(0.90, 0.95), 2)
                max_price = round(modal_price * random.uniform(1.05, 1.10), 2)

                # 5. Buffer Stock Logic (Crucial for your ML Model)
                # When stock is HIGH, Price is LOW (Inverse relationship)
                # Base stock ~5000 tonnes +/- random
                stock_impact = (base - modal_price) * 100 # If price is high, stock is likely low
                buffer_stock = int(5000 + stock_impact + random.randint(-500, 500))
                buffer_stock = max(0, buffer_stock)

                row = {
                    "commodity": name,
                    "variety": details["variety"],
                    "grade": "FAQ", # Fair Average Quality
                    "min_price": min_price,
                    "modal_price": modal_price,
                    "max_price": max_price,
                    "date": date_str,
                    "state": mkt["state"],
                    "district": mkt["district"],
                    "market": mkt["market"],
                    "buffer_stock_qty_kg": buffer_stock
                }
                data.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle rows so it looks like real collected data
    df = df.sample(frac=1).reset_index(drop=True)
    
    print(f"📊 Generated {len(df)} rows.")
    
    # Save
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved to: {OUTPUT_FILE}")
    print("👉 Now run 'python -m src.training.train_model' to re-train your AI with this new data!")

if __name__ == "__main__":
    generate_data()