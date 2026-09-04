import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. Load dataset
# ==========================================

df = pd.read_csv("data/merged_multi_wind_data.csv")

print("Dataset loaded!")
print("Total rows:", len(df))


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
# 3. Same train/test split as training
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42
)


# ==========================================
# 4. Load trained model
# ==========================================

model = joblib.load("models/wind_model.pkl")

print("\nTrained model loaded!")


# ==========================================
# 5. Prediction
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 6. Evaluation
# ==========================================

mae = mean_absolute_error(y_test, y_pred)

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(y_test, y_pred)


# ==========================================
# 7. Results
# ==========================================

print("\n========================================")
print("       WIND MODEL VALIDATION")
print("========================================")

print(f"MAE  : {mae:.2f} kWh")
print(f"RMSE : {rmse:.2f} kWh")
print(f"R²   : {r2:.4f}")


# ==========================================
# 8. Actual vs Predicted examples
# ==========================================

result = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_pred
})

print("\nFirst 10 predictions:")
print(result.head(10).to_string(index=False))


# ==========================================
# 9. Range check
# ==========================================

print("\n========================================")
print("          RANGE CHECK")
print("========================================")

print(f"Actual minimum    : {y_test.min():.2f} kWh")
print(f"Actual maximum    : {y_test.max():.2f} kWh")

print(f"Predicted minimum : {y_pred.min():.2f} kWh")
print(f"Predicted maximum : {y_pred.max():.2f} kWh")