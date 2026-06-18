"""
Dataset Generator: Amazon Sale Report (Synthetic)
Generates realistic e-commerce data matching the Amazon Sale Report structure.
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

CATEGORIES = {
    "Set":           ["Kurta Set", "Ethnic Set", "Casual Set", "Party Set"],
    "kurta":         ["Printed Kurta", "Solid Kurta", "Embroidered Kurta", "Rayon Kurta"],
    "Western Dress": ["Maxi Dress", "Mini Dress", "Midi Dress", "Wrap Dress"],
    "Top":           ["Crop Top", "Off Shoulder Top", "Tunic Top", "Printed Top"],
    "Blouse":        ["Silk Blouse", "Cotton Blouse", "Designer Blouse", "Plain Blouse"],
    "Bottom":        ["Palazzo", "Trouser", "Legging", "Skirt"],
    "Dupatta":       ["Chiffon Dupatta", "Cotton Dupatta", "Silk Dupatta"],
    "Saree":         ["Silk Saree", "Cotton Saree", "Designer Saree"],
    "Ethnic Dress":  ["Anarkali", "Lehenga Choli", "Salwar Suit"],
    "Jacket":        ["Denim Jacket", "Bomber Jacket", "Blazer"],
}

SIZES   = ["XS","S","M","L","XL","XXL","3XL","4XL","5XL","6XL","Free"]
STATES  = [
    "Maharashtra","Karnataka","Delhi","Tamil Nadu","Uttar Pradesh",
    "Gujarat","Rajasthan","West Bengal","Telangana","Andhra Pradesh",
    "Haryana","Punjab","Madhya Pradesh","Kerala","Bihar",
    "Odisha","Assam","Jharkhand","Uttarakhand","Chhattisgarh",
]
CITIES = {
    "Maharashtra":   ["Mumbai","Pune","Nagpur","Nashik"],
    "Karnataka":     ["Bangalore","Mysore","Hubli","Mangalore"],
    "Delhi":         ["New Delhi","Delhi"],
    "Tamil Nadu":    ["Chennai","Coimbatore","Madurai","Salem"],
    "Uttar Pradesh": ["Lucknow","Kanpur","Agra","Varanasi"],
    "Gujarat":       ["Ahmedabad","Surat","Vadodara","Rajkot"],
    "Rajasthan":     ["Jaipur","Jodhpur","Udaipur","Kota"],
    "West Bengal":   ["Kolkata","Durgapur","Asansol","Siliguri"],
    "Telangana":     ["Hyderabad","Warangal","Nizamabad","Karimnagar"],
    "Andhra Pradesh":["Vijayawada","Visakhapatnam","Guntur","Tirupati"],
    "Haryana":       ["Gurugram","Faridabad","Panipat","Rohtak"],
    "Punjab":        ["Ludhiana","Amritsar","Jalandhar","Patiala"],
    "Madhya Pradesh":["Bhopal","Indore","Jabalpur","Gwalior"],
    "Kerala":        ["Thiruvananthapuram","Kochi","Kozhikode","Thrissur"],
    "Bihar":         ["Patna","Gaya","Bhagalpur","Muzaffarpur"],
    "Odisha":        ["Bhubaneswar","Cuttack","Rourkela","Brahmapur"],
    "Assam":         ["Guwahati","Silchar","Dibrugarh","Jorhat"],
    "Jharkhand":     ["Ranchi","Jamshedpur","Dhanbad","Bokaro"],
    "Uttarakhand":   ["Dehradun","Haridwar","Roorkee","Haldwani"],
    "Chhattisgarh":  ["Raipur","Bhilai","Korba","Bilaspur"],
}
STATUSES    = ["Shipped","Delivered","Cancelled","Returned","Pending","Shipped - Delivered to Buyer"]
CHANNELS    = ["Amazon.in","Non-Amazon"]
FULFILMENTS = ["Amazon","Merchant"]
COURIERS    = ["Easy Ship","Bluedart","DTDC","Delhivery","Ekart"]

def random_date(start="2022-03-01", end="2022-06-30"):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end,   "%Y-%m-%d")
    return s + timedelta(days=random.randint(0, (e - s).days))

def gen_order_id():
    return f"405-{random.randint(1000000,9999999)}-{random.randint(1000000,9999999)}"

def gen_asin():
    return "B0" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))

N = 50000
rows = []
for i in range(N):
    cat   = random.choice(list(CATEGORIES.keys()))
    style = random.choice(CATEGORIES[cat])
    state = random.choices(STATES, weights=[15,12,10,9,8,7,6,5,5,5,4,4,3,3,3,2,2,2,2,2])[0]
    city  = random.choice(CITIES[state])
    status= random.choices(STATUSES, weights=[40,30,10,8,8,4])[0]
    qty   = random.choices([1,2,3,4,5], weights=[60,25,8,4,3])[0]
    price = round(random.uniform(199, 2999), 2)
    amount= round(price * qty, 2)
    if random.random() < 0.04: amount = np.nan
    if random.random() < 0.03: city   = np.nan
    if random.random() < 0.02: state  = np.nan
    if random.random() < 0.02: status = np.nan

    rows.append({
        "index":              i + 1,
        "Order ID":           gen_order_id(),
        "Date":               random_date().strftime("%m-%d-%Y"),
        "Status":             status,
        "Fulfilment":         random.choices(FULFILMENTS, weights=[75,25])[0],
        "Sales Channel ":     random.choices(CHANNELS, weights=[90,10])[0],
        "ship-service-level": random.choices(["Expedited","Standard"], weights=[60,40])[0],
        "Style":              style,
        "SKU":                f"SKU-{random.randint(10000,99999)}",
        "Category":           cat,
        "Size":               random.choice(SIZES),
        "ASIN":               gen_asin(),
        "Courier Status":     random.choices(COURIERS, weights=[30,20,15,25,10])[0],
        "Qty":                qty,
        "currency":           "INR",
        "Amount":             amount,
        "ship-city":          city,
        "ship-state":         state,
        "ship-postal-code":   random.randint(110001, 999999),
        "ship-country":       "IN",
        "promotion-ids":      random.choice([np.nan,"Amazon SPOT","IN Core Free Shipping"]),
        "B2B":                random.choices([True, False], weights=[10,90])[0],
        "fulfilled-by":       random.choice(["Easy Ship", np.nan]),
    })

df = pd.DataFrame(rows)
dup_idx = np.random.choice(len(df), 200, replace=False)
df = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

out = "/home/claude/E-Commerce-BI-Platform/Dataset/Amazon_Sale_Report.csv"
df.to_csv(out, index=False)
print(f"Dataset saved → {out}")
print(f"Shape: {df.shape}")
