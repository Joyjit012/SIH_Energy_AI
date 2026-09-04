import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
df = pd.read_csv("data/solar_data.csv")

# Input features
X = df[
    [
        "temperature",
        "direct_radiation",
        "diffuse_radiation"
    ]
]

# Target
y = df["solar_generation"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42
)

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

# Create Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# Train
print("\nTraining model...")
model.fit(X_train, y_train)

print("Training completed!")

# Prediction
y_pred = model.predict(X_test)

# Evaluation
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\n===== MODEL RESULT =====")
print("RMSE:", rmse)
print("R2 Score:", r2)