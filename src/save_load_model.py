import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. Load dataset
# ==========================================
df = pd.read_csv("data/load_data.csv")

print("Training final Load model...")

# ==========================================
# 2. Convert timestamp
# ==========================================
df["utc_timestamp"] = pd.to_datetime(
    df["utc_timestamp"],
    utc=True
)

# ==========================================
# 3. Create time features
# ==========================================
df["hour"] = df["utc_timestamp"].dt.hour
df["day_of_week"] = df["utc_timestamp"].dt.dayofweek
df["month"] = df["utc_timestamp"].dt.month
df["day_of_year"] = df["utc_timestamp"].dt.dayofyear

# ==========================================
# 4. Features and target
# ==========================================
features = [
    "hour",
    "day_of_week",
    "month",
    "day_of_year"
]

X = df[features]
y = df["load"]

# ==========================================
# 5. Train final model using all data
# ==========================================
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

print("Training completed!")

# ==========================================
# 6. Create models folder
# ==========================================
os.makedirs("models", exist_ok=True)

# ==========================================
# 7. Save model
# ==========================================
model_path = "models/load_model.pkl"

joblib.dump(model, model_path)

print("\nLoad model saved successfully!")
print("File:", model_path)