# ==========================================
# AUSTRIA WEATHER API
# SOLAR + WIND ML PREDICTION
# ==========================================

import requests
import pandas as pd
import joblib


# ==========================================
# 1. AUSTRIAN CITIES
# ==========================================

CITIES = {
    "vienna": (48.2082, 16.3738),
    "graz": (47.0707, 15.4395),
    "linz": (48.3069, 14.2858),
    "salzburg": (47.8095, 13.0550),
    "innsbruck": (47.2692, 11.4041),
    "klagenfurt": (46.6247, 14.3053)
}


# ==========================================
# 2. GET WEATHER DATA
# ==========================================

def get_city_weather(city, latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": [
            "temperature_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "direct_radiation",
            "diffuse_radiation"
        ],

        "timezone": "UTC",

        # 16-day forecast
        "forecast_days": 16
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["hourly"]


# ==========================================
# 3. FETCH ALL CITIES
# ==========================================

def get_austria_weather():

    print("\n========================================")
    print("      FETCHING AUSTRIA WEATHER")
    print("========================================")

    city_data = {}

    for city, coordinates in CITIES.items():

        latitude = coordinates[0]
        longitude = coordinates[1]

        print(f"\nFetching {city.upper()}...")

        weather = get_city_weather(
            city,
            latitude,
            longitude
        )

        city_data[city] = weather

        print(
            f"{city.upper()} data received: "
            f"{len(weather['time'])} hours"
        )

    return city_data


# ==========================================
# 4. CREATE MODEL INPUT
# ==========================================

def create_prediction_dataframe(city_data):

    # ======================================
    # Time
    # ======================================

    timestamps = city_data["vienna"]["time"]

    df = pd.DataFrame({
        "utc_timestamp": pd.to_datetime(
            timestamps,
            utc=True
        )
    })


    # ======================================
    # SOLAR FEATURES
    # ======================================

    df["temperature"] = (
        city_data["vienna"]["temperature_2m"]
    )

    df["direct_radiation"] = (
        city_data["vienna"]["direct_radiation"]
    )

    df["diffuse_radiation"] = (
        city_data["vienna"]["diffuse_radiation"]
    )


    # ======================================
    # WIND FEATURES
    # ======================================

    for city in CITIES:

        weather = city_data[city]

        df[f"{city}_temperature"] = (
            weather["temperature_2m"]
        )

        df[f"{city}_pressure"] = (
            weather["surface_pressure"]
        )

        df[f"{city}_wind_speed"] = (
            weather["wind_speed_10m"]
        )

        df[f"{city}_wind_direction"] = (
            weather["wind_direction_10m"]
        )

    return df


# ==========================================
# 5. LOAD ML MODELS
# ==========================================

def load_models():

    print("\n========================================")
    print("          LOADING ML MODELS")
    print("========================================")

    solar_model = joblib.load(
        "models/solar_model.pkl"
    )

    wind_model = joblib.load(
        "models/wind_model.pkl"
    )

    print("Solar model loaded!")
    print("Wind model loaded!")

    return solar_model, wind_model


# ==========================================
# 6. GENERATE PREDICTIONS
# ==========================================

def generate_predictions(df):

    solar_model, wind_model = load_models()


    # ======================================
    # SOLAR PREDICTION
    # ======================================

    solar_input = df[
        [
            "temperature",
            "direct_radiation",
            "diffuse_radiation"
        ]
    ]

    solar_prediction = solar_model.predict(
        solar_input
    )

    df["solar_prediction"] = (
        solar_prediction.clip(min=0)
    )


    # ======================================
    # WIND PREDICTION
    # ======================================

    wind_features = (
        wind_model.feature_names_in_
    )

    wind_input = df[
        wind_features
    ]

    wind_prediction = wind_model.predict(
        wind_input
    )

    df["wind_prediction"] = (
        wind_prediction.clip(min=0)
    )


    # ======================================
    # TOTAL RENEWABLE
    # ======================================

    df["total_renewable"] = (
        df["solar_prediction"]
        +
        df["wind_prediction"]
    )


    return df


# ==========================================
# 7. MAIN TEST
# ==========================================

if __name__ == "__main__":

    city_data = get_austria_weather()

    prediction_df = (
        create_prediction_dataframe(
            city_data
        )
    )

    prediction_df = generate_predictions(
        prediction_df
    )


    # ======================================
    # DISPLAY RESULTS
    # ======================================

    print("\n========================================")
    print("       24-HOUR RENEWABLE FORECAST")
    print("========================================")

    print(
        prediction_df[
            [
                "utc_timestamp",
                "solar_prediction",
                "wind_prediction",
                "total_renewable"
            ]
        ].to_string(index=False)
    )


    # ======================================
    # SAVE FORECAST
    # ======================================

    output_file = (
        "data/"
        "api_renewable_forecast.csv"
    )

    prediction_df.to_csv(
        output_file,
        index=False
    )

    print("\n========================================")
    print("Forecast saved:")
    print(output_file)
    print("========================================")