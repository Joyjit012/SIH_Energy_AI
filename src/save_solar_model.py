import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

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

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42
)

# Create model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# Train model
print("Training model...")
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "models/solar_model.pkl")

print("Solar model saved successfully!")