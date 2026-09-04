import pandas as pd

df = pd.read_csv("data/solar_data.csv")

print("===== DATASET INFO =====")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DUPLICATE ROWS =====")
print(df.duplicated().sum())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== SOLAR GENERATION =====")
print(df["solar_generation"].describe())