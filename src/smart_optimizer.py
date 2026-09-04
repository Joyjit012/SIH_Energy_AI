# ==========================================
# SMART ENERGY OPTIMIZER - TEST
# ==========================================

import sys

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
# BATTERY CONFIGURATION
# ==========================================

battery_capacity = 10000
initial_soc = 50

stored_energy = initialize_battery(
    battery_capacity,
    initial_soc
)

initial_energy = stored_energy


# ==========================================
# TEST INPUT
# ==========================================

solar = 100
wind = 100
load = 10000


# ==========================================
# RUN
# ==========================================

result = manage_energy(
    solar=solar,
    wind=wind,
    load=load,
    stored_energy=stored_energy,
    battery_capacity=battery_capacity
)


# ==========================================
# DISPLAY
# ==========================================

print("\n========================================")
print("       SMART ENERGY OPTIMIZER")
print("========================================")

print("Solar              :", solar, "kWh")
print("Wind               :", wind, "kWh")

print(
    "Renewable          :",
    round(result["renewable"], 2),
    "kWh"
)

print("Load               :", load, "kWh")


# ==========================================
# LOAD PRIORITY
# ==========================================

print("\n----- LOAD PRIORITY -----")

print(
    "Critical Load      :",
    round(result["critical_load"], 2),
    "kWh"
)

print(
    "Important Load     :",
    round(result["important_load"], 2),
    "kWh"
)

print(
    "Flexible Load      :",
    round(result["flexible_load"], 2),
    "kWh"
)


# ==========================================
# ENERGY FLOW
# ==========================================

print("\n----- ENERGY FLOW -----")

print(
    "Renewable -> Load   :",
    round(result["renewable_to_load"], 2),
    "kWh"
)

print(
    "Flexible Reduction :",
    round(result["flexible_reduction"], 2),
    "kWh"
)

print(
    "Battery Used       :",
    round(result["battery_used"], 2),
    "kWh"
)

print(
    "Battery Charged    :",
    round(result["battery_charged"], 2),
    "kWh"
)

print(
    "Generator          :",
    round(result["generator"], 2),
    "kWh"
)

print(
    "Curtailed          :",
    round(result["curtailed"], 2),
    "kWh"
)


# ==========================================
# BATTERY
# ==========================================

print("\n----- BATTERY -----")

print(
    "Initial Energy     :",
    round(initial_energy, 2),
    "kWh"
)

print(
    "Stored Energy      :",
    round(result["stored_energy"], 2),
    "kWh"
)

print(
    "SOC                :",
    round(result["soc"], 2),
    "%"
)


# ==========================================
# SMART MANAGEMENT
# ==========================================

print("\n----- SMART MANAGEMENT -----")

print(
    "Original Load      :",
    load,
    "kWh"
)

print(
    "Optimized Load     :",
    round(
        result["optimized_load"],
        2
    ),
    "kWh"
)

print(
    "Action             :",
    result["action"]
)


# ==========================================
# ENERGY BALANCE
# ==========================================

print("\n----- ENERGY BALANCE -----")

energy_supplied = (
    result["renewable_to_load"]
    + result["battery_used"]
    + result["generator"]
)

optimized_demand = (
    result["optimized_load"]
)

balance_error = (
    energy_supplied -
    optimized_demand
)

print(
    "Energy Supplied    :",
    round(energy_supplied, 2),
    "kWh"
)

print(
    "Optimized Demand   :",
    round(optimized_demand, 2),
    "kWh"
)

print(
    "Balance Error      :",
    round(balance_error, 2),
    "kWh"
)

if abs(balance_error) < 0.01:

    print(
        "Status             : BALANCED ✓"
    )

else:

    print(
        "Status             : CHECK REQUIRED"
    )


print("========================================")