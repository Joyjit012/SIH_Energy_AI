import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ==========================================
# 1. Load data
# ==========================================
df = pd.read_csv("data/load_data.csv")

print("Load dataset loaded!")
print("Total rows:", len(df))

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
# 4. Features
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
# 5. Train/Test split
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
# 6. Create model
# ==========================================
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# ==========================================
# 7. Train
# ==========================================
print("\nTraining Load model...")

model.fit(X_train, y_train)

print("Load model training completed!")

# ==========================================
# 8. Predict
# ==========================================
y_pred = model.predict(X_test)

# ==========================================
# 9. Evaluate
# ==========================================
rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)

print("\n===== LOAD MODEL RESULT =====")
print("RMSE:", rmse)
print("R2 Score:", r2)