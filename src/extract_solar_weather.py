import pandas as pd

input_file = "data/weather_data.csv"
output_file = "data/solar_weather.csv"

print("Reading weather data...")

columns = [
    "utc_timestamp",
    "AT_temperature",
    "AT_radiation_direct_horizontal",
    "AT_radiation_diffuse_horizontal"
]

df = pd.read_csv(
    input_file,
    usecols=columns
)

print("\nData loaded successfully!")
print("Rows:", len(df))
print("\nFirst 5 rows:")
print(df.head())

# Save only required columns
df.to_csv(output_file, index=False)

print("\nSolar weather data saved!")
print("File:", output_file)