import pandas as pd
import numpy as np
import copy
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import pickle

# Import data
initial_traffic_volume = pd.read_csv('Train.csv')

# Data preprocessing
# Splitting date-time into Year, Month, Day, Hour
initial_traffic_volume['date_time'] = pd.to_datetime(initial_traffic_volume['date_time'])
initial_traffic_volume['year'] = initial_traffic_volume['date_time'].dt.year
initial_traffic_volume['month'] = initial_traffic_volume['date_time'].dt.month
initial_traffic_volume['day'] = initial_traffic_volume['date_time'].dt.day
initial_traffic_volume['hour'] = initial_traffic_volume['date_time'].dt.hour

# Make a copy of the dataframe
init_traffic_volume = initial_traffic_volume.copy()

# Dropping unnecessary columns
traffic_volume = initial_traffic_volume.drop(
    ['date_time', "air_pollution_index", 'visibility_in_miles', 'rain_p_h', 
     'dew_point', 'snow_p_h', 'weather_description', 'is_holiday', 'year'], axis=1
)

# Mapping weather type to numeric values
traffic_volume['weather_type'] = traffic_volume['weather_type'].map({
    'Clouds': 1, 'Clear': 2, 'Mist': 3, 'Rain': 4, 'Snow': 5, 
    'Drizzle': 6, 'Haze': 7, 'Fog': 8, 'Thunderstorm': 9, 
    'Smoke': 10, 'Squall': 11
})

# Reorganizing columns
traffic_volume = traffic_volume[
    ['month', 'day', 'hour', 'humidity', 'wind_speed', 'wind_direction', 
     'temperature', 'clouds_all', 'weather_type', 'traffic_volume']
]

# Binning traffic volume data into 3 levels
labels_traffic = [0, 1, 2]
traffic_volume['traffic_vol'] = pd.qcut(
    traffic_volume['traffic_volume'], q=3, labels=labels_traffic
)

# Dropping the original traffic volume column
traffic_volume = traffic_volume.drop(['traffic_volume'], axis=1)

# Normalization of data
standardScaler = StandardScaler()

# Transform features and explicitly cast the result to float64
scaled_features = pd.DataFrame(
    standardScaler.fit_transform(traffic_volume.iloc[:, :-1]),
    columns=traffic_volume.columns[:-1],
    dtype='float64'  # Ensure data type is compatible
)

# Combine the scaled features with the target column
traffic_volume = pd.concat([scaled_features, traffic_volume['traffic_vol']], axis=1)

# Splitting data into features (X) and target (y)
X = traffic_volume.iloc[:, :-1]
y = traffic_volume.iloc[:, -1]

# Train Random Forest Model
clf = RandomForestClassifier(n_estimators=110, random_state=42)

# Train the model using the training data
clf.fit(X, y)

# Save the trained model
pickle.dump(clf, open('model.pkl', 'wb'))

# Optional: Load the model to test
# model = pickle.load(open('model.pkl', 'rb'))
# print(model.predict([[10, 2, 9, 89, 2, 329, 288.28, 40, 1]]))
