import pandas as pd

class DataCleaner:
    
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        df = pd.read_csv(csv_path = "D:\avfs303_backend\dataset\commodity_dataset.csv")


        # Convert date
        df['date'] = pd.to_datetime(df['date'])

        # Convert numbers and force errors to NaN
        df['price_retail'] = pd.to_numeric(df['price_retail'], errors='coerce')
        df['buffer_stock_qty_kg'] = pd.to_numeric(df['buffer_stock_qty_kg'], errors='coerce')

        # Remove rows with missing price / date
        df.dropna(subset=['date', 'price_retail'], inplace=True)

        return df
