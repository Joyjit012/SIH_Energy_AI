import pandas as pd

# ==========================================
# LOAD RESULTS
# ==========================================

df = pd.read_csv(
    "data/energy_management_results.csv"
)

print("\n========================================")
print("       ENERGY SYSTEM VALIDATION")
print("========================================")

print("\nTotal rows:", len(df))


# ==========================================
# RENEWABLE STATISTICS
# ==========================================

print("\n===== SOLAR =====")

print(
    "Average:",
    round(df["solar_prediction"].mean(), 2),
    "kWh"
)

print(
    "Maximum:",
    round(df["solar_prediction"].max(), 2),
    "kWh"
)

print(
    "Minimum:",
    round(df["solar_prediction"].min(), 2),
    "kWh"
)


print("\n===== WIND =====")

print(
    "Average:",
    round(df["wind_prediction"].mean(), 2),
    "kWh"
)

print(
    "Maximum:",
    round(df["wind_prediction"].max(), 2),
    "kWh"
)

print(
    "Minimum:",
    round(df["wind_prediction"].min(), 2),
    "kWh"
)


# ==========================================
# LOAD STATISTICS
# ==========================================

print("\n===== LOAD =====")

print(
    "Average:",
    round(df["load_prediction"].mean(), 2),
    "kWh"
)

print(
    "Maximum:",
    round(df["load_prediction"].max(), 2),
    "kWh"
)

print(
    "Minimum:",
    round(df["load_prediction"].min(), 2),
    "kWh"
)


# ==========================================
# BATTERY STATISTICS
# ==========================================

print("\n===== BATTERY =====")

charging_hours = (
    df["battery_charged"] > 0
).sum()

discharging_hours = (
    df["battery_used"] > 0
).sum()

print(
    "Charging hours:",
    charging_hours
)

print(
    "Discharging hours:",
    discharging_hours
)

print(
    "Maximum SOC:",
    round(
        df["battery_soc"].max(),
        2
    ),
    "%"
)

print(
    "Minimum SOC:",
    round(
        df["battery_soc"].min(),
        2
    ),
    "%"
)


# ==========================================
# GENERATOR
# ==========================================

print("\n===== GENERATOR =====")

generator_hours = (
    df["generator"] > 0
).sum()

print(
    "Generator ON hours:",
    generator_hours
)

print(
    "Total generator energy:",
    round(
        df["generator"].sum(),
        2
    ),
    "kWh"
)


# ==========================================
# CURTAILMENT
# ==========================================

print("\n===== CURTAILMENT =====")

curtailed_hours = (
    df["curtailed"] > 0
).sum()

print(
    "Curtailment hours:",
    curtailed_hours
)

print(
    "Total curtailed:",
    round(
        df["curtailed"].sum(),
        2
    ),
    "kWh"
)


# ==========================================
# FINAL
# ==========================================

print("\n========================================")
print("             CHECK COMPLETE")
print("========================================")