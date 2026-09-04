import pandas as pd

input_file = "data/time_series_60min_singleindex.csv"
output_file = "data/solar_generation.csv"

print("Reading solar generation data...")

df = pd.read_csv(
    input_file,
    usecols=[
        "utc_timestamp",
        "AT_solar_generation_actual"
    ]
)

print("Data loaded!")
print("Rows:", len(df))

print("\nFirst 5 rows:")
print(df.head())

df.to_csv(output_file, index=False)

print("\nSolar generation data saved!")
print("File:", output_file)