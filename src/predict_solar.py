import joblib

# Load trained model
model = joblib.load("models/solar_model.pkl")

# Example weather conditions
temperature = 10
direct_radiation = 200
diffuse_radiation = 100

# Prediction
prediction = model.predict([
    [temperature, direct_radiation, diffuse_radiation]
])

print("Predicted Solar Power:", prediction[0], "MW")