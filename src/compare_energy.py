import sys
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ==========================================
# LOAD RESULTS
# ==========================================

df = pd.read_csv(
    "data/energy_management_results.csv"
)

# ==========================================
# BASELINE GENERATOR
# ==========================================
# যদি battery না থাকত,
# renewable দিয়ে load supply করার পর
# যত shortage থাকত সেটাই generator demand

df["baseline_generator"] = (
    df["load_prediction"] -
    df["total_renewable"]
).clip(lower=0)


# ==========================================
# SMART GENERATOR
# ==========================================

df["smart_generator"] = (
    df["generator"]
)


# ==========================================
# GENERATOR SAVING
# ==========================================

baseline_total = df["baseline_generator"].sum()

smart_total = df["smart_generator"].sum()

generator_saving = (
    baseline_total -
    smart_total
)

saving_percent = (
    generator_saving /
    baseline_total
) * 100


# ==========================================
# BATTERY STATISTICS
# ==========================================

total_charged = df["battery_charged"].sum()

total_used = df["battery_used"].sum()

charging_hours = (
    df["battery_charged"] > 0
).sum()

discharging_hours = (
    df["battery_used"] > 0
).sum()


# ==========================================
# RENEWABLE UTILIZATION
# ==========================================

total_renewable = df["total_renewable"].sum()

renewable_used = (
    df["total_renewable"] -
    df["curtailed"]
).sum()

renewable_utilization = (
    renewable_used /
    total_renewable
) * 100


# ==========================================
# RESULTS
# ==========================================

print("\n")
print("========================================")
print("       SMART ENERGY VALIDATION")
print("========================================")

print("\n===== GENERATOR =====")

print(
    "Baseline Generator :",
    round(baseline_total, 2),
    "kWh"
)

print(
    "Smart Generator    :",
    round(smart_total, 2),
    "kWh"
)

print(
    "Generator Saving   :",
    round(generator_saving, 2),
    "kWh"
)

print(
    "Saving Percentage  :",
    round(saving_percent, 4),
    "%"
)


print("\n===== BATTERY =====")

print(
    "Total Charged      :",
    round(total_charged, 2),
    "kWh"
)

print(
    "Total Discharged   :",
    round(total_used, 2),
    "kWh"
)

print(
    "Charging Hours     :",
    charging_hours
)

print(
    "Discharging Hours  :",
    discharging_hours
)


print("\n===== RENEWABLE =====")

print(
    "Total Renewable    :",
    round(total_renewable, 2),
    "kWh"
)

print(
    "Renewable Used     :",
    round(renewable_used, 2),
    "kWh"
)

print(
    "Renewable Util.    :",
    round(renewable_utilization, 2),
    "%"
)

print("\n========================================")
print("             CHECK COMPLETE")
print("========================================")
