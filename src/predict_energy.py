# ==========================================
# SMART ENERGY MANAGEMENT
# ML PREDICTION + ENERGY OPTIMIZATION
# ==========================================

import os
import sys
import pandas as pd
import joblib

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from energy_manager import (
    initialize_battery,
    manage_energy
)


# ==========================================
# 1. BATTERY CONFIGURATION
# ==========================================

print("\n===== BATTERY CONFIGURATION =====")

if "--auto" in sys.argv or not sys.stdin.isatty():
    battery_capacity = 500000.0
    initial_soc = 100.0
    print(f"Auto mode activated: Battery Capacity = {battery_capacity} kWh (500 MWh), Initial SOC = {initial_soc}%")
else:
    try:
        cap_in = input("Enter battery capacity (kWh, default 500000): ").strip()
        battery_capacity = float(cap_in) if cap_in else 500000.0
        soc_in = input("Enter initial battery SOC (%, default 100): ").strip()
        initial_soc = float(soc_in) if soc_in else 100.0
    except Exception:
        battery_capacity = 500000.0
        initial_soc = 100.0

# Validate battery capacity

if battery_capacity <= 0:

    raise ValueError(
        "Battery capacity must be greater than 0."
    )


# Initialize battery

stored_energy = initialize_battery(
    battery_capacity,
    initial_soc
)

initial_energy = stored_energy

print(
    "Initial stored energy:",
    round(initial_energy, 2),
    "kWh"
)


# ==========================================
# 2. LOAD ML MODELS
# ==========================================

print("\nLoading ML models...")

solar_model = joblib.load(
    "models/solar_model.pkl"
)

wind_model = joblib.load(
    "models/wind_model.pkl"
)

load_model = joblib.load(
    "models/load_model.pkl"
)

print(
    "All models loaded successfully!"
)


# ==========================================
# 3. LOAD DATASETS
# ==========================================

print("\nLoading actual datasets...")

solar_df = pd.read_csv(
    "data/solar_weather.csv"
)

wind_df = pd.read_csv(
    "data/wind_weather_multi.csv"
)

load_df = pd.read_csv(
    "data/load_data.csv"
)

print(
    "Actual datasets loaded!"
)


# ==========================================
# 4. TIMESTAMP CONVERSION
# ==========================================

print("\nConverting timestamps...")

solar_df["utc_timestamp"] = pd.to_datetime(
    solar_df["utc_timestamp"],
    utc=True
)

wind_df["utc_timestamp"] = pd.to_datetime(
    wind_df["utc_timestamp"],
    utc=True
)

load_df["utc_timestamp"] = pd.to_datetime(
    load_df["utc_timestamp"],
    utc=True
)


# ==========================================
# 5. MERGE DATASETS
# ==========================================

print("\nMerging datasets...")

df = solar_df.merge(
    wind_df,
    on="utc_timestamp",
    how="inner"
)

df = df.merge(
    load_df,
    on="utc_timestamp",
    how="inner"
)

df = (
    df
    .sort_values(
        "utc_timestamp"
    )
    .reset_index(drop=True)
)

print(
    "Common timestamps:",
    len(df)
)

if len(df) == 0:

    raise ValueError(
        "No common timestamps found "
        "between datasets."
    )


# ==========================================
# 6. SOLAR PREDICTION
# ==========================================

print("\nPredicting solar generation...")

solar_input = pd.DataFrame({

    "temperature":
        df["AT_temperature"],

    "direct_radiation":
        df[
            "AT_radiation_direct_horizontal"
        ],

    "diffuse_radiation":
        df[
            "AT_radiation_diffuse_horizontal"
        ]
})

solar_predictions = (
    solar_model.predict(
        solar_input
    )
)

print(
    "Solar prediction completed!"
)


# ==========================================
# 7. WIND PREDICTION
# ==========================================

print("\nPredicting wind generation...")

# Use exactly the features
# used during model training

if hasattr(
    wind_model,
    "feature_names_in_"
):

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
            + str(missing_features)
        )

    wind_input = df[
        wind_features
    ]

else:

    raise ValueError(
        "Wind model does not contain "
        "feature_names_in_."
    )


wind_predictions = (
    wind_model.predict(
        wind_input
    )
)

print(
    "Wind prediction completed!"
)


# ==========================================
# 8. LOAD PREDICTION
# ==========================================

print("\nPredicting load demand...")

timestamps = df[
    "utc_timestamp"
]

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

load_predictions = (
    load_model.predict(
        load_input
    )
)

print(
    "Load prediction completed!"
)


# ==========================================
# 9. ADD PREDICTIONS
# ==========================================

df["solar_prediction"] = (
    solar_predictions
)

df["wind_prediction"] = (
    wind_predictions
)

df["load_prediction"] = (
    load_predictions
)


# ==========================================
# 10. SMART ENERGY SIMULATION
# ==========================================

print(
    "\n========================================"
)

print(
    "Starting SMART energy simulation..."
)

print(
    "========================================"
)

results = []

total_rows = len(df)


for index, row in df.iterrows():

    # ======================================
    # PREDICTED VALUES
    # ======================================

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


    # ======================================
    # SMART ENERGY MANAGER
    # ======================================

    result = manage_energy(

        solar=solar,

        wind=wind,

        load=load,

        stored_energy=stored_energy,

        battery_capacity=battery_capacity

    )


    # ======================================
    # UPDATE BATTERY
    # ======================================

    # Very important:
    # Current hour's battery state
    # becomes next hour's battery state.

    stored_energy = (
        result["stored_energy"]
    )


    # ======================================
    # SAVE RESULT
    # ======================================

    results.append({

        "utc_timestamp":
            row["utc_timestamp"],

        # ------------------------------
        # Predictions
        # ------------------------------

        "solar_prediction":
            solar,

        "wind_prediction":
            wind,

        "load_prediction":
            load,

        "total_renewable":
            result["renewable"],


        # ------------------------------
        # Load Priority
        # ------------------------------

        "critical_load":
            result["critical_load"],

        "important_load":
            result["important_load"],

        "flexible_load":
            result["flexible_load"],


        # ------------------------------
        # Renewable → Load
        # ------------------------------

        "renewable_to_load":
            result["renewable_to_load"],


        # ------------------------------
        # Flexible Load
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
        # Battery
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
        # Generator
        # ------------------------------

        "generator":
            result[
                "generator"
            ],


        # ------------------------------
        # Curtailment
        # ------------------------------

        "curtailed":
            result[
                "curtailed"
            ],


        # ------------------------------
        # Total Load Supplied
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
        # Decision
        # ------------------------------

        "action":
            result[
                "action"
            ]

    })


    # ======================================
    # PROGRESS
    # ======================================

    if (
        (index + 1) % 5000 == 0
        or
        index == total_rows - 1
    ):

        print(
            f"Processed: "
            f"{index + 1} / "
            f"{total_rows}"
        )


# ==========================================
# 11. RESULT DATAFRAME
# ==========================================

results_df = pd.DataFrame(
    results
)


# ==========================================
# 12. SAVE CSV
# ==========================================

output_file = "data/energy_management_results.csv"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
results_df.to_csv(
    output_file,
    index=False
)


# ==========================================
# 13. FINAL SOC
# ==========================================

final_soc = (
    stored_energy /
    battery_capacity
) * 100.0

final_soc = max(
    0.0,
    min(
        100.0,
        final_soc
    )
)


# ==========================================
# 14. FINAL SUMMARY
# ==========================================

print(
    "\n\n========================================"
)

print(
    "      SMART ENERGY MANAGEMENT"
)

print(
    "              COMPLETED"
)

print(
    "========================================"
)

print(
    "Total hours processed:",
    len(results_df)
)

print(
    "Initial SOC:",
    initial_soc,
    "%"
)

print(
    "Final SOC:",
    round(
        final_soc,
        2
    ),
    "%"
)


# ==========================================
# ENERGY
# ==========================================

print("\n===== ENERGY =====")

print(
    "Total Renewable:",
    round(
        results_df[
            "total_renewable"
        ].sum(),
        2
    ),
    "kWh"
)

print(
    "Total Generator:",
    round(
        results_df[
            "generator"
        ].sum(),
        2
    ),
    "kWh"
)


# ==========================================
# BATTERY
# ==========================================

print("\n===== BATTERY =====")

print(
    "Total Battery Charged:",
    round(
        results_df[
            "battery_charged"
        ].sum(),
        2
    ),
    "kWh"
)

print(
    "Total Battery Used:",
    round(
        results_df[
            "battery_used"
        ].sum(),
        2
    ),
    "kWh"
)

print(
    "Charging Hours:",
    (
        results_df[
            "battery_charged"
        ] > 0
    ).sum()
)

print(
    "Discharging Hours:",
    (
        results_df[
            "battery_used"
        ] > 0
    ).sum()
)


# ==========================================
# LOAD MANAGEMENT
# ==========================================

print(
    "\n===== LOAD MANAGEMENT ====="
)

print(
    "Total Flexible Load Reduction:",
    round(
        results_df[
            "flexible_reduction"
        ].sum(),
        2
    ),
    "kWh"
)

print(
    "Flexible Load Reduction Hours:",
    (
        results_df[
            "flexible_reduction"
        ] > 0
    ).sum()
)


# ==========================================
# CURTAILMENT
# ==========================================

print(
    "\n===== CURTAILMENT ====="
)

print(
    "Total Curtailed:",
    round(
        results_df[
            "curtailed"
        ].sum(),
        2
    ),
    "kWh"
)


# ==========================================
# OUTPUT
# ==========================================

print(
    "\nSaved as:",
    output_file
)

print(
    "========================================"
)