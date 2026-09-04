import pandas as pd
import joblib

# ==========================================
# 1. TEST TIMESTAMP
# ==========================================

timestamp = pd.Timestamp(
    "2025-01-15 12:00:00",
    tz="UTC"
)

hour = timestamp.hour
day_of_week = timestamp.dayofweek
month = timestamp.month
day_of_year = timestamp.dayofyear

print("===== PREDICTION INPUT =====")
print("Timestamp:", timestamp)
print("Hour:", hour)
print("Day of week:", day_of_week)
print("Month:", month)
print("Day of year:", day_of_year)


# ==========================================
# 2. SOLAR MODEL
# ==========================================

solar_model = joblib.load(
    "models/solar_model.pkl"
)

print("\n===== SOLAR MODEL LOADED =====")

solar_input = pd.DataFrame([{
    "temperature": -1.0,
    "direct_radiation": 100.0,
    "diffuse_radiation": 150.0
}])

solar_prediction = solar_model.predict(
    solar_input
)[0]

print(
    "Predicted Solar Generation:",
    round(solar_prediction, 2)
)


# ==========================================
# 3. WIND MODEL
# ==========================================

wind_model = joblib.load(
    "models/wind_model.pkl"
)

print("\n===== WIND MODEL LOADED =====")

wind_input = pd.DataFrame([{
    "vienna_temperature": -2.0,
    "vienna_pressure": 890.0,
    "vienna_wind_speed": 3.0,
    "vienna_wind_direction": 270.0,

    "graz_temperature": -2.5,
    "graz_pressure": 900.0,
    "graz_wind_speed": 2.5,
    "graz_wind_direction": 280.0,

    "linz_temperature": -1.5,
    "linz_pressure": 895.0,
    "linz_wind_speed": 3.2,
    "linz_wind_direction": 275.0,

    "salzburg_temperature": -3.0,
    "salzburg_pressure": 885.0,
    "salzburg_wind_speed": 2.8,
    "salzburg_wind_direction": 290.0,

    "innsbruck_temperature": -4.0,
    "innsbruck_pressure": 880.0,
    "innsbruck_wind_speed": 3.5,
    "innsbruck_wind_direction": 260.0,

    "klagenfurt_temperature": -2.0,
    "klagenfurt_pressure": 890.0,
    "klagenfurt_wind_speed": 2.7,
    "klagenfurt_wind_direction": 285.0
}])

wind_prediction = wind_model.predict(
    wind_input
)[0]

print(
    "Predicted Wind Generation:",
    round(wind_prediction, 2)
)


# ==========================================
# 4. LOAD MODEL
# ==========================================

load_model = joblib.load(
    "models/load_model.pkl"
)

print("\n===== LOAD MODEL LOADED =====")

load_input = pd.DataFrame([{
    "hour": hour,
    "day_of_week": day_of_week,
    "month": month,
    "day_of_year": day_of_year
}])

load_prediction = load_model.predict(
    load_input
)[0]

print(
    "Predicted Load:",
    round(load_prediction, 2)
)


# ==========================================
# 5. FINAL PREDICTION SUMMARY
# ==========================================

print("\n========================================")
print("       ENERGY PREDICTION SUMMARY")
print("========================================")

print(
    "Solar Generation :",
    round(solar_prediction, 2)
)

print(
    "Wind Generation  :",
    round(wind_prediction, 2)
)

print(
    "Total Renewable  :",
    round(solar_prediction + wind_prediction, 2)
)

print(
    "Load Demand      :",
    round(load_prediction, 2)
)

print("========================================")