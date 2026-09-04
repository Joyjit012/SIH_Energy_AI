import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ==========================================
# 1. Load dataset
# ==========================================
df = pd.read_csv("data/merged_multi_wind_data.csv")

print("Dataset loaded!")
print("Total rows:", len(df))

# ==========================================
# 2. Select weather features
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

# ==========================================
# 3. Target
# ==========================================

y = df["wind_generation"]

# ==========================================
# 4. Train / Test split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

# ==========================================
# 5. Random Forest model
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# ==========================================
# 6. Train
# ==========================================

print("\nTraining improved Wind model...")

model.fit(X_train, y_train)

print("Training completed!")

# ==========================================
# 7. Prediction
# ==========================================

y_pred = model.predict(X_test)

# ==========================================
# 8. Evaluation
# ==========================================

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)

print("\n===== IMPROVED WIND MODEL RESULT =====")
print("RMSE:", rmse)
print("R2 Score:", r2)