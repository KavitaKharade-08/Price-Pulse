import os
import joblib
import pandas as pd
import numpy as np
from prophet import Prophet
import warnings

warnings.filterwarnings("ignore")

# CONFIG (edit paths if needed)
MAIN_DATA_PATH = r"D:\avfs303_backend\dataset\commodity_dataset.csv"
WAREHOUSE_DATA_PATH = r"D:\avfs303_backend\dataset\sih_warehouse_data_1400.csv"
MODELS_DIR = r"D:\avfs303_backend\saved_models"

MIN_RECORDS = 20
DEFAULT_BUFFER_STOCK = 5000

os.makedirs(MODELS_DIR, exist_ok=True)


class ModelTrainer:
    def __init__(self,
                 main_path=MAIN_DATA_PATH,
                 warehouse_path=WAREHOUSE_DATA_PATH,
                 models_dir=MODELS_DIR,
                 min_records=MIN_RECORDS,
                 default_buffer=DEFAULT_BUFFER_STOCK):
        self.main_path = main_path
        self.warehouse_path = warehouse_path
        self.models_dir = models_dir
        self.min_records = min_records
        self.default_buffer = default_buffer

    # ---------- helpers ----------
    @staticmethod
    def safe_market_name(raw_market):
        if pd.isna(raw_market):
            return "Unknown_APMC"
        m = str(raw_market).strip().replace("/", "_").replace(" ", "_")
        if not m.upper().endswith("APMC"):
            m = m + "_APMC"
        return m

    @staticmethod
    def safe_filename(name: str):
        return str(name).replace(" ", "_").replace("/", "_")

    # ---------- load datasets ----------
    def load_main_dataset(self):
        if not os.path.exists(self.main_path):
            print(f"❌ Main dataset missing: {self.main_path}")
            return pd.DataFrame(columns=['date', 'commodity', 'market', 'price', 'buffer_stock_qty_kg'])

        df = pd.read_csv(self.main_path)
        df.columns = df.columns.str.strip().str.lower()

        # unify columns
        # prefer modal_price but allow alternate names
        price_col = None
        for c in ['modal_price', 'price', 'price_retail', 'max_price']:
            if c in df.columns:
                price_col = c
                break

        if price_col is None:
            print("❌ No price column in main dataset.")
            df['price'] = np.nan
        else:
            df['price'] = pd.to_numeric(df[price_col], errors='coerce')

        # normalize other columns
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce', infer_datetime_format=True)
        else:
            df['date'] = pd.NaT

        # commodity column
        if 'commodity' not in df.columns and 'commodity_name' in df.columns:
            df['commodity'] = df['commodity_name']
        # market column
        if 'market' not in df.columns:
            if 'centre_name' in df.columns:
                df['market'] = df['centre_name']
            elif 'market_name' in df.columns:
                df['market'] = df['market_name']
            else:
                df['market'] = 'Unknown'

        # buffer stock
        if 'buffer_stock_qty_kg' not in df.columns:
            df['buffer_stock_qty_kg'] = self.default_buffer
        else:
            df['buffer_stock_qty_kg'] = pd.to_numeric(df['buffer_stock_qty_kg'], errors='coerce').fillna(self.default_buffer)

        # reduce to needed cols
        df = df[['date', 'commodity', 'market', 'price', 'buffer_stock_qty_kg']]
        # drop rows missing essential values
        df = df.dropna(subset=['date', 'commodity', 'market'])
        return df

    def load_warehouse_dataset(self):
        # Warehouse dataset likely has no price; we will try to parse and skip rows without price
        if not os.path.exists(self.warehouse_path):
            return pd.DataFrame(columns=['date', 'commodity', 'market', 'price', 'buffer_stock_qty_kg'])

        df = pd.read_csv(self.warehouse_path)
        df.columns = df.columns.str.strip().str.lower()

        # entry_date -> date
        if 'entry_date' in df.columns:
            df['date'] = pd.to_datetime(df['entry_date'], errors='coerce', infer_datetime_format=True)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce', infer_datetime_format=True)
        else:
            df['date'] = pd.NaT

        # commodity column
        if 'commodity' not in df.columns and 'commodity_name' in df.columns:
            df['commodity'] = df['commodity_name']

        # market: create a descriptive market from location
        if 'location' in df.columns:
            df['market'] = df['location'].astype(str) + " Warehouse"
        else:
            df['market'] = 'Unknown Warehouse'

        # price: many warehouse datasets have no price -> leave NaN (we'll drop)
        price_col = None
        for c in ['modal_price', 'price', 'modalprice', 'modal price']:
            if c in df.columns:
                price_col = c
                break
        if price_col:
            df['price'] = pd.to_numeric(df[price_col], errors='coerce')
        else:
            df['price'] = np.nan

        # buffer stock from quantity fields
        if 'quantity_mt' in df.columns:
            df['buffer_stock_qty_kg'] = pd.to_numeric(df['quantity_mt'], errors='coerce').fillna(0) * 1000
        else:
            df['buffer_stock_qty_kg'] = self.default_buffer

        df = df[['date', 'commodity', 'market', 'price', 'buffer_stock_qty_kg']]
        # we cannot train from rows without price, so drop price-less rows
        df = df.dropna(subset=['date', 'commodity', 'market', 'price'])
        return df

    # ---------- merge and normalize ----------
    def load_and_prepare(self):
        main = self.load_main_dataset()
        ware = self.load_warehouse_dataset()
        combined = pd.concat([main, ware], ignore_index=True, sort=False)

        if combined.empty:
            print("❌ Combined dataset is empty after loading.")
            return combined

        # normalize commodity and market strings
        combined['commodity'] = combined['commodity'].astype(str).str.strip()
        combined['market'] = combined['market'].astype(str).apply(self.safe_market_name)

        # ensure price numeric
        combined['price'] = pd.to_numeric(combined['price'], errors='coerce')

        # drop rows missing required
        combined = combined.dropna(subset=['date', 'commodity', 'market', 'price'])

        # sort
        combined = combined.sort_values('date').reset_index(drop=True)
        return combined

    # ---------- train pipeline ----------
    def train_pipeline(self):
        df = self.load_and_prepare()
        if df.empty:
            print("❌ No data to train on.")
            return

        # group by normalized commodity & market
        pairs = df.groupby(['commodity', 'market']).size().reset_index(name='count')
        total_pairs = len(pairs)
        saved = 0

        for idx, row in pairs.iterrows():
            commodity = row['commodity']
            market = row['market']
            count = int(row['count'])

            if count < self.min_records:
                print(f"⚠️ Skipping {commodity} at {market}: only {count} records (need >= {self.min_records})")
                continue

            # subset for this pair
            subset = df[(df['commodity'] == commodity) & (df['market'] == market)].copy()
            subset = subset.rename(columns={'date': 'ds', 'price': 'y', 'buffer_stock_qty_kg': 'buffer_stock_qty_kg'})

            # ensure ds sorted
            subset = subset.sort_values('ds').reset_index(drop=True)

            # resample to daily frequency from min to max date
            start = subset['ds'].min().normalize()
            end = subset['ds'].max().normalize()
            if pd.isna(start) or pd.isna(end) or start >= end:
                print(f"⚠️ Bad date range for {commodity} at {market}. Skipping.")
                continue

            idx_range = pd.date_range(start=start, end=end, freq='D')
            # create daily frame
            daily = pd.DataFrame({'ds': idx_range})
            # merge existing values into daily
            merged = pd.merge(daily, subset[['ds', 'y', 'buffer_stock_qty_kg']], on='ds', how='left')

            # fill buffer stock: forward fill then fill remaining with default
            if 'buffer_stock_qty_kg' in merged.columns:
                merged['buffer_stock_qty_kg'] = merged['buffer_stock_qty_kg'].ffill().bfill().fillna(self.default_buffer)
            else:
                merged['buffer_stock_qty_kg'] = self.default_buffer

            # fill y by interpolation (linear), then forward/back fill as fallback
            merged['y'] = pd.to_numeric(merged['y'], errors='coerce')
            merged['y'] = merged['y'].interpolate(method='linear', limit_direction='both')
            merged['y'] = merged['y'].ffill().bfill()

            # drop rows still missing y
            merged = merged.dropna(subset=['y'])
            if len(merged) < self.min_records:
                print(f"⚠️ After resampling, not enough points for {commodity} at {market} ({len(merged)}). Skipping.")
                continue

            # Configure Prophet - choose a stable number of changepoints relative to data size
            n_changepoints = min(25, max(1, len(merged) // 7))  # roughly one changepoint per week of data, capped at 25
            try:
                m = Prophet(daily_seasonality=True, yearly_seasonality=True,
                            n_changepoints=n_changepoints, changepoint_range=0.8)
                # add regressor
                m.add_regressor('buffer_stock_qty_kg')

                # fit
                m.fit(merged[['ds', 'y', 'buffer_stock_qty_kg']])
            except Exception as e:
                print(f"❌ Failed to train model for {commodity} at {market}: {e}")
                continue

            # save model
            safe_name = f"{self.safe_filename(commodity)}_{market}"
            model_path = os.path.join(self.models_dir, f"{safe_name}.pkl")
            try:
                joblib.dump(m, model_path)
                saved += 1
                print(f"Saved: {model_path} ({saved}/{total_pairs})")
            except Exception as e:
                print(f"❌ Failed to save model for {commodity} at {market}: {e}")

        print(f"\n✅ Training Finished → {saved} models saved out of {total_pairs}")


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_pipeline()
