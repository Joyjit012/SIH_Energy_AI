# ==========================================
# SMART AI ENERGY MANAGEMENT
# 7-DAY API FORECAST ENGINE
# SINGLE DATE + DATE RANGE READY
# ==========================================

import sys
import os
import pandas as pd
import numpy as np
import joblib

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from weather_api import (
    get_city_weather,
    CITIES,
    create_prediction_dataframe
)

from energy_manager import (
    initialize_battery,
    manage_energy
)


# ==========================================
# 1. LOAD ML MODELS
# ==========================================

print("\n========================================")
print("          LOADING ML MODELS")
print("========================================")

solar_model = joblib.load(
    "models/solar_model.pkl"
)

wind_model = joblib.load(
    "models/wind_model.pkl"
)

load_model = joblib.load(
    "models/load_model.pkl"
)

print("Solar model loaded!")
print("Wind model loaded!")
print("Load model loaded!")


# ==========================================
# 2. FETCH 7-DAY WEATHER
# ==========================================

def get_weather_7_days():

    print("\n========================================")
    print("      FETCHING 7-DAY AUSTRIA WEATHER")
    print("========================================")

    city_data = {}

    for city, coordinates in CITIES.items():

        latitude = coordinates[0]
        longitude = coordinates[1]

        print(
            f"\nFetching {city.upper()}..."
        )

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
# 3. CREATE WEATHER DATAFRAME
# ==========================================

def create_weather_dataframe():

    city_data = get_weather_7_days()

    df = create_prediction_dataframe(
        city_data
    )

    df["utc_timestamp"] = pd.to_datetime(
        df["utc_timestamp"],
        utc=True
    )

    df = (
        df
        .sort_values("utc_timestamp")
        .reset_index(drop=True)
    )

    print("\nTotal weather records:")

    print(
        len(df),
        "hours"
    )

    return df


# ==========================================
# 4. PREDICT SOLAR + WIND + LOAD
# ==========================================

def predict_generation(df):

    print(
        "\n========================================"
    )

    print(
        "          RUNNING ML PREDICTIONS"
    )

    print(
        "========================================"
    )


    # ======================================
    # SOLAR PREDICTION
    # ======================================

    solar_input = pd.DataFrame({

        "temperature":
            df["temperature"],

        "direct_radiation":
            df["direct_radiation"],

        "diffuse_radiation":
            df["diffuse_radiation"]
    })

    solar_prediction = (
        solar_model.predict(
            solar_input
        )
    )

    df["solar_prediction"] = (
        np.maximum(
            solar_prediction,
            0
        )
    )

    print(
        "Solar prediction completed!"
    )


    # ======================================
    # WIND PREDICTION
    # ======================================

    wind_features = (
        wind_model.feature_names_in_
    )

    missing_features = [

        feature

        for feature in wind_features

        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing wind features: "
            +
            str(missing_features)
        )

    wind_input = df[
        wind_features
    ]

    wind_prediction = (
        wind_model.predict(
            wind_input
        )
    )

    df["wind_prediction"] = (
        np.maximum(
            wind_prediction,
            0
        )
    )

    print(
        "Wind prediction completed!"
    )


    # ======================================
    # TOTAL RENEWABLE
    # ======================================

    df["total_renewable"] = (

        df["solar_prediction"]

        +

        df["wind_prediction"]
    )


    # ======================================
    # LOAD PREDICTION
    # ======================================

    timestamps = (
        df["utc_timestamp"]
    )

    load_input = pd.DataFrame({

        "hour":
            timestamps.dt.hour,

        "day_of_week":
            timestamps.dt.dayofweek,

        "month":
            timestamps.dt.month,

        "day_of_year":
            timestamps.dt.dayofyear
    })

    load_prediction = (
        load_model.predict(
            load_input
        )
    )

    df["load_prediction"] = (
        np.maximum(
            load_prediction,
            0
        )
    )

    print(
        "Load prediction completed!"
    )

    return df


# ==========================================
# 5. GET SINGLE DATE
# ==========================================

def get_single_date(
    df,
    date
):

    date = pd.Timestamp(
        date,
        tz="UTC"
    ).normalize()

    next_date = (
        date +
        pd.Timedelta(days=1)
    )

    daily_df = df[
        (
            df["utc_timestamp"]
            >= date
        )
        &
        (
            df["utc_timestamp"]
            < next_date
        )
    ].copy()

    return (
        daily_df
        .reset_index(drop=True)
    )


# ==========================================
# 6. RUN ENERGY MANAGEMENT
# ==========================================

def run_energy_management(
    df,
    battery_capacity,
    initial_soc
):

    # ======================================
    # INITIAL BATTERY
    # ======================================

    stored_energy = (
        initialize_battery(
            battery_capacity,
            initial_soc
        )
    )

    results = []


    # ======================================
    # PROCESS EACH HOUR
    # ======================================

    for _, row in df.iterrows():

        solar = max(
            0.0,
            float(
                row["solar_prediction"]
            )
        )

        wind = max(
            0.0,
            float(
                row["wind_prediction"]
            )
        )

        load = max(
            0.0,
            float(
                row["load_prediction"]
            )
        )


        # ==================================
        # SMART ENERGY MANAGER
        # ==================================

        result = manage_energy(

            solar=solar,

            wind=wind,

            load=load,

            stored_energy=stored_energy,

            battery_capacity=battery_capacity
        )


        # ==================================
        # CARRY BATTERY STATE
        # ==================================

        stored_energy = (
            result["stored_energy"]
        )


        # ==================================
        # SAVE HOURLY RESULT
        # ==================================

        results.append({

            # ------------------------------
            # TIME
            # ------------------------------

            "utc_timestamp":
                row["utc_timestamp"],

            "date":
                row["utc_timestamp"].strftime(
                    "%Y-%m-%d"
                ),

            "time":
                row["utc_timestamp"].strftime(
                    "%H:%M"
                ),


            # ------------------------------
            # ENERGY
            # ------------------------------

            "solar_prediction":
                solar,

            "wind_prediction":
                wind,

            "total_renewable":
                result[
                    "renewable"
                ],

            "load_prediction":
                load,


            # ------------------------------
            # LOAD PRIORITY
            # ------------------------------

            "critical_load":
                result[
                    "critical_load"
                ],

            "important_load":
                result[
                    "important_load"
                ],

            "flexible_load":
                result[
                    "flexible_load"
                ],


            # ------------------------------
            # RENEWABLE → LOAD
            # ------------------------------

            "renewable_to_load":
                result[
                    "renewable_to_load"
                ],


            # ------------------------------
            # FLEXIBLE LOAD
            # ------------------------------

            "flexible_reduction":
                result[
                    "flexible_reduction"
                ],

            "optimized_load":
                result[
                    "optimized_load"
                ],


            # ------------------------------
            # BATTERY
            # ------------------------------

            "battery_charged":
                result[
                    "battery_charged"
                ],

            "battery_used":
                result[
                    "battery_used"
                ],

            "battery_stored":
                result[
                    "stored_energy"
                ],

            "battery_soc":
                result[
                    "soc"
                ],


            # ------------------------------
            # GENERATOR
            # ------------------------------

            "generator":
                result[
                    "generator"
                ],


            # ------------------------------
            # CURTAILMENT
            # ------------------------------

            "curtailed":
                result[
                    "curtailed"
                ],


            # ------------------------------
            # LOAD SUPPLIED
            # ------------------------------

            "load_supplied":

                (
                    result[
                        "renewable_to_load"
                    ]

                    +

                    result[
                        "battery_used"
                    ]

                    +

                    result[
                        "generator"
                    ]
                ),


            # ------------------------------
            # ACTION
            # ------------------------------

            "action":
                result[
                    "action"
                ]
        })


    return pd.DataFrame(
        results
    )


# ==========================================
# 7. PROCESS DATE RANGE
# ==========================================

def forecast_date_range(
    df,
    start_date,
    end_date,
    battery_capacity,
    initial_soc
):

    # ======================================
    # CONVERT DATES
    # ======================================

    start = pd.Timestamp(
        start_date,
        tz="UTC"
    ).normalize()

    end = pd.Timestamp(
        end_date,
        tz="UTC"
    ).normalize()


    # ======================================
    # VALIDATE DATE
    # ======================================

    if end < start:

        raise ValueError(
            "End date cannot be before "
            "start date."
        )


    # ======================================
    # SELECT DATE RANGE
    # ======================================

    selected_df = df[
        (
            df["utc_timestamp"]
            >= start
        )
        &
        (
            df["utc_timestamp"]
            <
            end +
            pd.Timedelta(days=1)
        )
    ].copy()


    # ======================================
    # CHECK DATA
    # ======================================

    if len(selected_df) == 0:

        raise ValueError(
            "Selected date/range is not "
            "available in API forecast."
        )


    # ======================================
    # PRINT RANGE
    # ======================================

    print(
        "\n========================================"
    )

    print(
        "        SELECTED FORECAST RANGE"
    )

    print(
        "========================================"
    )

    print(
        "Start:",
        start.strftime(
            "%Y-%m-%d"
        )
    )

    print(
        "End:",
        end.strftime(
            "%Y-%m-%d"
        )
    )

    print(
        "Hourly records:",
        len(selected_df)
    )


    # ======================================
    # RUN ENERGY MANAGEMENT
    # ======================================
    #
    # Battery continues from one hour
    # to the next and from one day
    # to the next.
    #
    # ======================================

    result_df = (
        run_energy_management(

            selected_df,

            battery_capacity,

            initial_soc
        )
    )


    return result_df


# ==========================================
# 8. SAVE RESULT
# ==========================================

def save_results(df):
    output_file = "data/date_range_forecast.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    hist_file = "data/energy_management_results.csv"
    if os.path.exists(hist_file):
        try:
            hist_df = pd.read_csv(hist_file)
            if "date" not in hist_df.columns and "utc_timestamp" in hist_df.columns:
                hist_df["date"] = pd.to_datetime(hist_df["utc_timestamp"]).dt.strftime("%Y-%m-%d")
                hist_df["time"] = pd.to_datetime(hist_df["utc_timestamp"]).dt.strftime("%H:%M")
            combined_df = pd.concat([hist_df, df], ignore_index=True).drop_duplicates(subset=["utc_timestamp"])
            combined_df.to_csv(output_file, index=False)
            frontend_data_dir = "frontend/data"
            os.makedirs(frontend_data_dir, exist_ok=True)
            combined_df.to_csv(os.path.join(frontend_data_dir, "date_range_forecast.csv"), index=False)
            print("\n========================================")
            print(f"Saved combined dataset with {len(combined_df)} hourly records across all dates!")
            print(" - " + output_file)
            print(" - " + os.path.join(frontend_data_dir, "date_range_forecast.csv"))
            print("========================================")
            return
        except Exception:
            pass

    df.to_csv(output_file, index=False)
    frontend_data_dir = "frontend/data"
    os.makedirs(frontend_data_dir, exist_ok=True)
    df.to_csv(os.path.join(frontend_data_dir, "date_range_forecast.csv"), index=False)
    print("\n========================================")
    print("Forecast saved to:")
    print(" - " + output_file)
    print(" - " + os.path.join(frontend_data_dir, "date_range_forecast.csv"))
    print("========================================")


# ==========================================
# 9. DATE-WISE SUMMARY
# ==========================================

def show_date_summary(df):

    summary = (
        df
        .groupby("date")
        .agg({

            "solar_prediction":
                "sum",

            "wind_prediction":
                "sum",

            "total_renewable":
                "sum",

            "load_prediction":
                "sum",

            "flexible_reduction":
                "sum",

            "generator":
                "sum",

            "battery_charged":
                "sum",

            "battery_used":
                "sum"

        })
        .reset_index()
    )


    print(
        "\n========================================"
    )

    print(
        "           DATE-WISE SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        summary.to_string(
            index=False
        )
    )


# ==========================================
# 10. MAIN
# ==========================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "     SMART AI ENERGY FORECAST"
    )

    print(
        "========================================"
    )


    # ======================================
    # FETCH WEATHER
    # ======================================

    weather_df = (
        create_weather_dataframe()
    )


    # ======================================
    # ML PREDICTIONS
    # ======================================

    prediction_df = (
        predict_generation(
            weather_df
        )
    )


    # ======================================
    # USER INPUT (WITH DEFAULT FALLBACKS)
    # ======================================

    avail_dates = prediction_df["utc_timestamp"].dt.strftime("%Y-%m-%d").unique()
    default_start = avail_dates[0] if len(avail_dates) > 0 else "2026-08-29"
    default_end = avail_dates[-1] if len(avail_dates) > 0 else "2026-09-03"

    if "--auto" in sys.argv or not sys.stdin.isatty():
        start_date = default_start
        end_date = default_end
        battery_capacity = 500000.0
        initial_soc = 100.0
        print(f"\nAuto mode activated using date range: {start_date} to {end_date}, Battery: {battery_capacity} kWh (500 MWh), SOC: {initial_soc}%")
    else:
        try:
            start_in = input(f"\nEnter START date (YYYY-MM-DD, default {default_start}): ").strip()
            start_date = start_in if start_in else default_start

            end_in = input(f"Enter END date (YYYY-MM-DD, default {default_end}): ").strip()
            end_date = end_in if end_in else default_end

            cap_in = input("Enter battery capacity (kWh, default 500000): ").strip()
            battery_capacity = float(cap_in) if cap_in else 500000.0

            soc_in = input("Enter initial battery SOC (%, default 100): ").strip()
            initial_soc = float(soc_in) if soc_in else 100.0
        except Exception:
            start_date = default_start
            end_date = default_end
            battery_capacity = 500000.0
            initial_soc = 100.0


    # ======================================
    # RUN FORECAST
    # ======================================

    result = forecast_date_range(

        prediction_df,

        start_date,

        end_date,

        battery_capacity,

        initial_soc
    )


    # ======================================
    # SAVE CSV
    # ======================================

    save_results(
        result
    )


    # ======================================
    # DATE SUMMARY
    # ======================================

    show_date_summary(
        result
    )


    # ======================================
    # RECORD COUNT
    # ======================================

    print(
        "\nTotal hourly records:",
        len(result)
    )

    print(
        "\nCompleted successfully!"
    )