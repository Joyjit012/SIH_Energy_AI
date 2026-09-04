import requests
import pandas as pd

# ==========================================
# Austria representative locations
# ==========================================
locations = {
    "vienna": (48.2082, 16.3738),
    "graz": (47.0707, 15.4395),
    "linz": (48.3069, 14.2858),
    "salzburg": (47.8095, 13.0550),
    "innsbruck": (47.2692, 11.4041),
    "klagenfurt": (46.6247, 14.3053)
}

start_date = "2015-01-01"
end_date = "2020-06-30"

all_data = None

for name, (latitude, longitude) in locations.items():

    print(f"\nDownloading weather for {name}...")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,surface_pressure,wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "ms",
        "timezone": "GMT"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Failed for {name}")
        print(response.text)
        continue

    data = response.json()

    df = pd.DataFrame({
        "utc_timestamp": data["hourly"]["time"],
        f"{name}_temperature": data["hourly"]["temperature_2m"],
        f"{name}_pressure": data["hourly"]["surface_pressure"],
        f"{name}_wind_speed": data["hourly"]["wind_speed_10m"],
        f"{name}_wind_direction": data["hourly"]["wind_direction_10m"]
    })

    if all_data is None:
        all_data = df
    else:
        all_data = pd.merge(
            all_data,
            df,
            on="utc_timestamp",
            how="inner"
        )

# ==========================================
# Save data
# ==========================================

output_file = "data/wind_weather_multi.csv"

all_data.to_csv(
    output_file,
    index=False
)

print("\n================================")
print("Multi-location wind weather ready!")
print("================================")

print("Rows:", len(all_data))
print("Columns:", len(all_data.columns))

print("\nFirst 5 rows:")
print(all_data.head())

print("\nSaved as:")
print(output_file)