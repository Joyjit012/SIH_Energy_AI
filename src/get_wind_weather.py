import requests
import pandas as pd

# Austria representative location
latitude = 47.5162
longitude = 14.5501

# Our wind generation data starts from 2015
start_date = "2015-01-01"
end_date = "2020-06-30"

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_date,
    "end_date": end_date,
    "hourly": "surface_pressure,wind_speed_10m,wind_direction_10m",
    "wind_speed_unit": "ms",
    "timezone": "GMT"
}

print("Downloading Austria wind weather data...")

response = requests.get(url, params=params)

if response.status_code != 200:
    print("Download failed!")
    print(response.text)
    exit()

data = response.json()

df = pd.DataFrame({
    "utc_timestamp": data["hourly"]["time"],
    "pressure": data["hourly"]["surface_pressure"],
    "wind_speed": data["hourly"]["wind_speed_10m"],
    "wind_direction": data["hourly"]["wind_direction_10m"]
})

df.to_csv("data/wind_weather.csv", index=False)

print("\nWind weather data downloaded successfully!")
print("Rows:", len(df))

print("\nFirst 5 rows:")
print(df.head())

print("\nSaved as: data/wind_weather.csv")