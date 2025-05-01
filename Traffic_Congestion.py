import numpy as np
import requests
import pickle
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the ML model
try:
    model = pickle.load(open('../api/model.pkl', 'rb'))
except FileNotFoundError:
    raise FileNotFoundError("Model file not found at '../api/model.pkl'. Ensure the path is correct.")
except Exception as e:
    raise RuntimeError(f"Error loading model: {str(e)}")

# Required features for the prediction model
features_col = ['month', 'day', 'hour', 'humidity', 'wind_speed', 'wind_direction', 'temp', 'clouds_all', 'weather_type']

def validate_features(data):
    """
    Validate and extract features from the input data.

    Args:
        data (dict): Input data containing features.

    Returns:
        list: Validated and extracted feature values.
    """
    missing_features = [feature for feature in features_col if feature not in data]
    if missing_features:
        raise KeyError(f"Missing required features: {', '.join(missing_features)}")
    return [float(data[feature]) for feature in features_col]

def predict_func(data):
    """
    Perform prediction based on input data dictionary.

    Args:
        data (dict): Input data containing the required features.

    Returns:
        dict: Prediction result with metadata (date, time, result, etc.).
    """
    try:
        features = validate_features(data)
        final_features = np.array(features).reshape(1, -1)  # Reshape to match model input
        prediction = model.predict(final_features)
        prediction_label = int(prediction[0])

        # Map prediction to result labels and colors
        result_map = {0: ("Low", "success"), 1: ("Medium", "warning"), 2: ("High", "danger")}
        result, colour = result_map.get(prediction_label, ("Unknown", "secondary"))

        return {
            'date': data.get('date', 'N/A'),
            'time': data.get('time', 'N/A'),
            'prediction': prediction_label,
            'result': result,
            'colour': colour
        }
    except KeyError as e:
        return {"error": f"Missing required feature: {str(e)}"}
    except Exception as e:
        return {"error": f"Prediction error: {str(e)}"}

def fetch_weather_data(endpoint):
    """
    Fetch weather data from a given endpoint.

    Args:
        endpoint (str): API endpoint URL.

    Returns:
        dict or list: Weather data returned by the API.
    """
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json().get('data', {})

@app.route('/predict', methods=["GET"])
def predict():
    try:
        # Fetch weather data
        curr_data = fetch_weather_data('http://127.0.0.1:5001/curr-weather')
        hourly_data = fetch_weather_data('http://127.0.0.1:5001/hour-forecast')
        daily_data = fetch_weather_data('http://127.0.0.1:5001/daily-forecast')

        # Prepare the response with predictions
        return jsonify({
            "code": 200,
            "data": {
                "current": predict_func(curr_data),
                "hourly": [predict_func(hour) for hour in hourly_data],
                "daily": [predict_func(day) for day in daily_data]
            }
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"code": 500, "message": f"Error contacting weather APIs: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5003, debug=True)
