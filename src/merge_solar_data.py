import pandas as pd

weather = pd.read_csv("data/solar_weather.csv")
generation = pd.read_csv("data/solar_generation.csv")

print("Weather rows:", len(weather))
print("Generation rows:", len(generation))

# Merge using common timestamp
solar_data = pd.merge(
    weather,
    generation,
    on="utc_timestamp",
    how="inner"
)

# Rename columns to simpler names
solar_data = solar_data.rename(columns={
    "AT_temperature": "temperature",
    "AT_radiation_direct_horizontal": "direct_radiation",
    "AT_radiation_diffuse_horizontal": "diffuse_radiation",
    "AT_solar_generation_actual": "solar_generation"
})

# Remove rows where required data is missing
solar_data = solar_data.dropna()

# Save final dataset
solar_data.to_csv("data/solar_data.csv", index=False)

print("\nFinal Solar Dataset Created!")
print("Rows:", len(solar_data))
print("\nColumns:")
print(solar_data.columns.tolist())

print("\nFirst 5 rows:")
print(solar_data.head())