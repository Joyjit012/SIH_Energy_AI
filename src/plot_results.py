import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# LOAD ENERGY MANAGEMENT RESULTS
# ==========================================

df = pd.read_csv(
    "data/energy_management_results.csv"
)

df["utc_timestamp"] = pd.to_datetime(
    df["utc_timestamp"],
    utc=True
)


# ==========================================
# DAILY AGGREGATION
# ==========================================

daily = df.set_index("utc_timestamp").resample("D").agg({

    "solar_prediction": "sum",
    "wind_prediction": "sum",
    "load_prediction": "sum",

    "battery_charged": "sum",
    "battery_used": "sum",

    "battery_soc": "last",

    "generator": "sum"

}).reset_index()


daily["total_renewable"] = (
    daily["solar_prediction"]
    + daily["wind_prediction"]
)


# ==========================================
# GRAPH 1
# SOLAR + WIND
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    daily["utc_timestamp"],
    daily["solar_prediction"],
    label="Solar Generation"
)

plt.plot(
    daily["utc_timestamp"],
    daily["wind_prediction"],
    label="Wind Generation"
)

plt.title(
    "Daily Solar and Wind Energy Generation"
)

plt.xlabel("Date")
plt.ylabel("Energy (kWh/day)")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "data/graph_solar_wind.png",
    dpi=200
)

plt.show()


# ==========================================
# GRAPH 2
# RENEWABLE vs LOAD
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    daily["utc_timestamp"],
    daily["total_renewable"],
    label="Total Renewable"
)

plt.plot(
    daily["utc_timestamp"],
    daily["load_prediction"],
    label="Load Demand"
)

plt.title(
    "Renewable Energy vs Load Demand"
)

plt.xlabel("Date")
plt.ylabel("Energy (kWh/day)")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "data/graph_renewable_vs_load.png",
    dpi=200
)

plt.show()


# ==========================================
# GRAPH 3
# BATTERY SOC
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    daily["utc_timestamp"],
    daily["battery_soc"],
    label="Battery SOC"
)

plt.axhline(
    20,
    linestyle="--",
    label="Minimum SOC (20%)"
)

plt.title(
    "Battery State of Charge"
)

plt.xlabel("Date")
plt.ylabel("SOC (%)")

plt.ylim(0, 100)

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "data/graph_battery_soc.png",
    dpi=200
)

plt.show()


# ==========================================
# GRAPH 4
# LOAD vs RENEWABLE vs GENERATOR
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    daily["utc_timestamp"],
    daily["load_prediction"],
    label="Load Demand"
)

plt.plot(
    daily["utc_timestamp"],
    daily["total_renewable"],
    label="Total Renewable"
)

plt.plot(
    daily["utc_timestamp"],
    daily["generator"],
    label="Generator Output"
)

plt.title(
    "Load Demand vs Renewable Energy vs Generator"
)

plt.xlabel("Date")
plt.ylabel("Energy (kWh/day)")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "data/graph_energy_balance.png",
    dpi=200
)

plt.show()


# ==========================================
# COMPLETE
# ==========================================

print("\n========================================")
print("       ALL GRAPHS GENERATED")
print("========================================")

print(
    "1. data/graph_solar_wind.png"
)

print(
    "2. data/graph_renewable_vs_load.png"
)

print(
    "3. data/graph_battery_soc.png"
)

print(
    "4. data/graph_energy_balance.png"
)

print("\nDone!")