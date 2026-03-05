import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("market_data.db")
cursor = conn.cursor()

products = ["WIDGET-A", "GADGET-B", "SENSOR-C"]

start_date = datetime(2024,1,1)
num_days = 90

sale_id = 1
intel_id = 1
cursor.execute("DELETE FROM sales_history")
cursor.execute("DELETE FROM competitor_intelligence")
for product in products:

    base_price = random.uniform(20,50)

    for i in range(num_days):

        date = start_date + timedelta(days=i)

        price = round(base_price + random.uniform(-5,5),2)

        units_sold = max(1, int(30 - price*0.4 + random.uniform(-3,3)))

        promotion = random.choice([0,0,0,1])

        competitor_price = round(price + random.uniform(-3,3),2)

        cursor.execute("""
        INSERT INTO sales_history 
        (sale_id, date, product_id, units_sold, price, promotion_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,(sale_id, date.strftime("%Y-%m-%d"), product, units_sold, price, promotion))

        cursor.execute("""
        INSERT INTO competitor_intelligence
        (intel_id, product_id, competitor_price, timestamp)
        VALUES (?, ?, ?, ?)
        """,(intel_id, product, competitor_price, date.strftime("%Y-%m-%d")))

        sale_id += 1
        intel_id += 1
        print(date, product)
conn.commit()
conn.close()

print("Synthetic data generated successfully.")