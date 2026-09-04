import pandas as pd

input_file = "data/time_series_60min_singleindex.csv"
output_file = "data/load_data.csv"

print("Reading Austria load data...")

df = pd.read_csv(
    input_file,
    usecols=[
        "utc_timestamp",
        "AT_load_actual_entsoe_transparency"
    ]
)

# Rename column
df = df.rename(
    columns={
        "AT_load_actual_entsoe_transparency": "load"
    }
)

# Remove missing values
df = df.dropna()

# Convert timestamp
df["utc_timestamp"] = pd.to_datetime(
    df["utc_timestamp"],
    utc=True
)

# Sort by time
df = df.sort_values("utc_timestamp")

# Reset index
df = df.reset_index(drop=True)

# Save
df.to_csv(
    output_file,
    index=False
)

print("\n===== LOAD DATA READY =====")
print("Rows:", len(df))

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nSaved as:")
print(output_file)