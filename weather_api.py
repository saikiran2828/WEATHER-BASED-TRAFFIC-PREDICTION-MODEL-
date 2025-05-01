import requests
import datetime
import statistics
from flask import Flask, request, jsonify

app = Flask(__name__)

lat = 1.3521
long = 103.8198
api_key = "ve907d2bc4c8bc43a1b7b161620251823"  # Replace with your WeatherAPI key

weather_map = {
    'Clouds': 1,
    'Clear': 2,
    'Mist': 3,
    'Rain': 4,
    'Snow': 5,
    'Drizzle': 6,
    'Haze': 7,
    'Fog': 8,
    'Thunderstorm': 9,
    'Smoke': 10,
    'Squall': 11
}

# Function to retrieve month, day, and hour
def retrieve_datetime(unix):
    month = datetime.datetime.utcfromtimestamp(unix).strftime('%m')
    day = datetime.datetime.utcfromtimestamp(unix).strftime('%d')
    hour = datetime.datetime.utcfromtimestamp(unix).strftime('%H')
    return month, day, hour

@app.route('/')
def home():
    return jsonify({'message': 'Successful!'})

# API that retrieves current weather data
@app.route('/curr-weather', methods=['GET'])
def current():
    res_weather = requests.get(
        f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{long}"
    ).json()

    if "current" in res_weather:
        curr_weather = res_weather['current']
        location = res_weather['location']
        date_time = retrieve_datetime(location["localtime_epoch"])
        weather_type = curr_weather['condition']['text']
        return jsonify({
            "code": 200,
            "data": {
                "date": location["localtime"].split(' ')[0],
                "time": location["localtime"].split(' ')[1],
                "month": date_time[0],
                "day": date_time[1],
                "hour": date_time[2],
                "temp": curr_weather.get('temp_c', 0),
                "humidity": curr_weather.get('humidity', 0),
                "wind_speed": curr_weather.get('wind_kph', 0),
                "wind_direction": curr_weather.get('wind_degree', 0),
                "clouds_all": curr_weather.get('cloud', 0),
                "weather_type": weather_map.get(weather_type, 0)
            }
        })
    return jsonify({"code": 404, "message": "Error retrieving current weather data."}), 404

# API that retrieves hourly forecast data
@app.route('/hour-forecast', methods=['GET'])
def hour():
    res_weather = requests.get(
        f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{long}&days=1&hourly=1"
    ).json()

    if "forecast" in res_weather and "forecastday" in res_weather["forecast"]:
        hourly_forecast = res_weather['forecast']['forecastday'][0]['hour']
        forecast_list = []
        for forecast in hourly_forecast:
            date_time = retrieve_datetime(forecast["time_epoch"])
            weather_type = forecast['condition']['text']
            forecast_list.append({
                "date": forecast["time"].split(' ')[0],
                "time": forecast["time"].split(' ')[1],
                "month": date_time[0],
                "day": date_time[1],
                "hour": date_time[2],
                "temp": forecast.get('temp_c', 0),
                "humidity": forecast.get('humidity', 0),
                "wind_speed": forecast.get('wind_kph', 0),
                "wind_direction": forecast.get('wind_degree', 0),
                "clouds_all": forecast.get('cloud', 0),
                "weather_type": weather_map.get(weather_type, 0)
            })
        return jsonify({"code": 200, "data": forecast_list})
    return jsonify({"code": 404, "message": "Error retrieving hourly forecast data."}), 404

# API that retrieves daily forecast data
@app.route('/daily-forecast', methods=['GET'])
def daily():
    res_weather = requests.get(
        f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{long}&days=7"
    ).json()

    if "forecast" in res_weather and "forecastday" in res_weather["forecast"]:
        daily_forecast = res_weather['forecast']['forecastday']
        forecast_list = []
        for forecast in daily_forecast:
            date_time = retrieve_datetime(forecast["date_epoch"])
            weather_type = forecast['day']['condition']['text']
            forecast_list.append({
                "date": forecast["date"],
                "time": "12:00:00",  # WeatherAPI does not provide hourly details for daily data
                "month": date_time[0],
                "day": date_time[1],
                "hour": "12",  # Defaulting to noon
                "temp": forecast['day'].get('avgtemp_c', 0),
                "humidity": forecast['day'].get('avghumidity', 0),
                "wind_speed": forecast['day'].get('maxwind_kph', 0),
                "wind_direction": 0,  # Not available in daily data
                "clouds_all": forecast['day'].get('cloud', 0),
                "weather_type": weather_map.get(weather_type, 0)
            })
        return jsonify({"code": 200, "data": forecast_list})
    return jsonify({"code": 404, "message": "Error retrieving daily forecast data."}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)
