import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. Load dataset
# ==========================================
df = pd.read_csv("data/merged_multi_wind_data.csv")

# ==========================================
# 2. Features
# ==========================================
features = [
    "vienna_temperature",
    "vienna_pressure",
    "vienna_wind_speed",
    "vienna_wind_direction",

    "graz_temperature",
    "graz_pressure",
    "graz_wind_speed",
    "graz_wind_direction",

    "linz_temperature",
    "linz_pressure",
    "linz_wind_speed",
    "linz_wind_direction",

    "salzburg_temperature",
    "salzburg_pressure",
    "salzburg_wind_speed",
    "salzburg_wind_direction",

    "innsbruck_temperature",
    "innsbruck_pressure",
    "innsbruck_wind_speed",
    "innsbruck_wind_direction",

    "klagenfurt_temperature",
    "klagenfurt_pressure",
    "klagenfurt_wind_speed",
    "klagenfurt_wind_direction"
]

X = df[features]
y = df["wind_generation"]

# ==========================================
# 3. Train final model using all data
# ==========================================
print("Training final Wind model...")

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

print("Training completed!")

# ==========================================
# 4. Create models folder
# ==========================================
import os

os.makedirs("models", exist_ok=True)

# ==========================================
# 5. Save model
# ==========================================
model_path = "models/wind_model.pkl"

joblib.dump(model, model_path)

print("\nWind model saved successfully!")
print("File:", model_path)