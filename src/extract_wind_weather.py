import pandas as pd

input_file = "data/weather_data.csv"

print("Reading column names...")

df = pd.read_csv(input_file, nrows=5)

print("\n===== ALL COLUMNS =====")

for column in df.columns:
    print(column)