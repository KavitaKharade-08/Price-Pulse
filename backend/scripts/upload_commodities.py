import csv
from firebase_config import db
from datetime import datetime

# Open the CSV file
with open('commodity_dataset2.csv', 'r') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        # Skip rows where min_price, modal_price, or max_price are empty
        if not row['min_price'] or not row['modal_price'] or not row['max_price']:
            continue

        # Convert price_date to datetime (MM/DD/YYYY)
        try:
            price_date = datetime.strptime(row['date'], '%m/%d/%Y')
        except:
            price_date = None

        # Add row to Firestore
        db.collection('commodities').add({
            "commodity": row['commodity'],
            "variety": row['variety'],
            "grade": row['grade'],
            "min_price": float(row['min_price']),
            "modal_price": float(row['modal_price']),
            "max_price": float(row['max_price']),
            "price_date": price_date,
            "state": row['state'],
            "district": row['district'],
            "market": row['market']
        })

print("All commodities uploaded successfully!")
