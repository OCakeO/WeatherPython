import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
import calendar
hourly_dataframe = ()
daily_data = {}
def weather_in_city(latitudeCity, longitudeCity):
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": latitudeCity,
		"longitude": longitudeCity,
		"hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation_probability", "precipitation", "cloud_cover", "visibility", "wind_speed_10m", "uv_index"],
		"daily": ["temperature_2m_max", "temperature_2m_min"],
		"wind_speed_unit": "ms",
		"timezone": "Europe/Moscow",
		"forecast_days": 16
	}
	responses = openmeteo.weather_api(url, params=params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation {response.Elevation()} m asl")
	print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
	hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
	hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
	hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(5).ValuesAsNumpy()
	hourly_visibility = hourly.Variables(6).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()
	hourly_uv_index = hourly.Variables(8).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}
	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["apparent_temperature"] = hourly_apparent_temperature
	hourly_data["precipitation_probability"] = hourly_precipitation_probability
	hourly_data["precipitation"] = hourly_precipitation
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["visibility"] = hourly_visibility
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
	hourly_data["uv_index"] = hourly_uv_index

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	# print(hourly_dataframe)

	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
		end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min

	# daily_dataframe = pd.DataFrame(data = daily_data)
	# print(daily_dataframe)
	mas_day = []
	mas_hour = []
	for date in daily_data['date']:
		mas_day.append(f"{date.day} {transform_date(date.month)}")
	
	current_daily_data = {
		"date" : mas_day,
		"temperature_2m_max": daily_data["temperature_2m_max"].astype(int),
		"temperature_2m_min" : daily_data["temperature_2m_min"].astype(int)
	}

	for hour in hourly_data["date"]:
		mas_hour.append(f"{hour.hour}:{hour.minute}")
	
	hourly_data_split = []
	for i in range(0, len(hourly_data["date"]), 24):
		chunk = {
			"hour": [f"{(hour.hour + 3) % 24}:00" for hour in hourly_data["date"][i:i+24]],
			"temp": hourly_data["temperature_2m"][i:i+24].astype(int),
			"humidity": hourly_data["relative_humidity_2m"][i:i+24].astype(int),
			"apparent_temp": hourly_data["apparent_temperature"][i:i+24].astype(int),
			"precipitation_prob": hourly_data["precipitation_probability"][i:i+24].astype(int),
			"precipitation": hourly_data["precipitation"][i:i+24].astype(int),
			"cloud_cover": hourly_data["cloud_cover"][i:i+24].astype(int),
			"visibility": hourly_data["visibility"][i:i+24].astype(int)/1000,
			"wind_speed": hourly_data["wind_speed_10m"][i:i+24].astype(int),
			"uv_index": hourly_data["uv_index"][i:i+24]
		}
		hourly_data_split.append(chunk)
		# print(hourly_data_split)

	return hourly_data_split, current_daily_data

def transform_date(date):

    months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня','Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
    return months[int(date) - 1]

# weather_in_city(54.875, 53.0625)