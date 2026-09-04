import pandas as pd

# ==========================================
# File paths
# ==========================================
weather_file = "data/wind_weather_multi.csv"
generation_file = "data/time_series_60min_singleindex.csv"
output_file = "data/merged_multi_wind_data.csv"

print("Reading multi-location wind weather data...")
weather = pd.read_csv(weather_file)

print("Reading wind generation data...")
generation = pd.read_csv(
    generation_file,
    usecols=[
        "utc_timestamp",
        "AT_wind_onshore_generation_actual"
    ]
)

# ==========================================
# Fix timestamps
# ==========================================
weather["utc_timestamp"] = pd.to_datetime(
    weather["utc_timestamp"],
    utc=True
)

generation["utc_timestamp"] = pd.to_datetime(
    generation["utc_timestamp"],
    utc=True
)

generation = generation.rename(
    columns={
        "AT_wind_onshore_generation_actual": "wind_generation"
    }
)

# ==========================================
# Remove missing generation
# ==========================================
generation = generation.dropna(
    subset=["wind_generation"]
)

print("Merging data...")

merged = pd.merge(
    weather,
    generation,
    on="utc_timestamp",
    how="inner"
)

# ==========================================
# Remove duplicates
# ==========================================
merged = merged.drop_duplicates(
    subset=["utc_timestamp"]
)

# ==========================================
# Save
# ==========================================
merged.to_csv(
    output_file,
    index=False
)

print("\n================================")
print("MULTI-LOCATION WIND DATA READY")
print("================================")

print("Rows:", len(merged))
print("Columns:", len(merged.columns))

print("\nColumns:")
print(merged.columns.tolist())

print("\nMissing values:")
print(merged.isnull().sum())

print("\nFirst 5 rows:")
print(merged.head())

print("\nSaved successfully!")
print("File:", output_file)