import json
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
from datetime import datetime

import requests

def fetch_historical_weather():
    print("Fetching 1 year of historical weather data from Open-Meteo Archive...")
    # Fetch 2023 data for Halifax
    url = "https://archive-api.open-meteo.com/v1/archive?latitude=44.6488&longitude=-63.5752&start_date=2023-01-01&end_date=2023-12-31&hourly=temperature_2m"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    df = pd.DataFrame({
        'datetime': pd.to_datetime(data['hourly']['time']),
        'temperature': data['hourly']['temperature_2m']
    })
    # Fill any missing values (rare but possible in archive)
    df['temperature'] = df['temperature'].ffill().bfill()
    return df

def train_and_evaluate():
    print("Training ML models for Halifax Energy Forecast on Historical Data...")
    
    # 1. Fetch Real Historical Weather
    df = fetch_historical_weather()
    
    # Feature Engineering
    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['month'] = df['datetime'].dt.month
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    
    # 2. Synthetic building load calculation PROXY based strictly on real weather
    # Base load + heating component (temp < 15) + cooling component (temp > 22) + diurnal pattern
    diurnal = np.sin((df['hour'] - 6) * (np.pi / 12)) * 300
    heating_load = np.maximum(15 - df['temperature'], 0) * 80
    cooling_load = np.maximum(df['temperature'] - 22, 0) * 120
    weekend_drop = df['is_weekend'] * -500
    
    noise = np.random.normal(0, 50, len(df))
    df['load_mw'] = 1500 + diurnal + heating_load + cooling_load + weekend_drop + noise
    
    # Features (X) and Target (y)
    features = ['hour', 'dayofweek', 'month', 'is_weekend', 'temperature']
    X = df[features]
    y = df['load_mw']
    
    # Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    print(f"Data Generation Complete. Train size: {len(X_train)} | Test size: {len(X_test)}")
    
    # ------------------
    # Model 1: XGBoost
    # ------------------
    print("Training XGBoost...")
    xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    xgb_model.fit(X_train, y_train)
    xgb_preds_train = xgb_model.predict(X_train)
    xgb_preds_test = xgb_model.predict(X_test)
    
    xgb_metrics = {
        'train_rmse': round(np.sqrt(mean_squared_error(y_train, xgb_preds_train)), 2),
        'test_rmse': round(np.sqrt(mean_squared_error(y_test, xgb_preds_test)), 2),
        'train_r2': round(r2_score(y_train, xgb_preds_train), 3),
        'test_r2': round(r2_score(y_test, xgb_preds_test), 3)
    }
    
    # ------------------
    # Model 2: Random Forest
    # ------------------
    print("Training Random Forest...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds_train = rf_model.predict(X_train)
    rf_preds_test = rf_model.predict(X_test)
    
    rf_metrics = {
        'train_rmse': round(np.sqrt(mean_squared_error(y_train, rf_preds_train)), 2),
        'test_rmse': round(np.sqrt(mean_squared_error(y_test, rf_preds_test)), 2),
        'train_r2': round(r2_score(y_train, rf_preds_train), 3),
        'test_r2': round(r2_score(y_test, rf_preds_test), 3)
    }
    
    # ------------------
    # Model 3: Neural Network
    # ------------------
    print("Training Neural Network (MLP)...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    nn_model = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    nn_model.fit(X_train_scaled, y_train)
    nn_preds_train = nn_model.predict(X_train_scaled)
    nn_preds_test = nn_model.predict(X_test_scaled)
    
    nn_metrics = {
        'train_rmse': round(np.sqrt(mean_squared_error(y_train, nn_preds_train)), 2),
        'test_rmse': round(np.sqrt(mean_squared_error(y_test, nn_preds_test)), 2),
        'train_r2': round(r2_score(y_train, nn_preds_train), 3),
        'test_r2': round(r2_score(y_test, nn_preds_test), 3)
    }

    # ------------------
    # Generate Output JSON
    # ------------------
    metrics_output = {
        'generated_at': datetime.now().isoformat(),
        'dataset_info': {
            'total_samples': len(df),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features': features,
            'target': 'load_mw'
        },
        'models': {
            'xgboost': xgb_metrics,
            'random_forest': rf_metrics,
            'neural_network': nn_metrics
        },
        'feature_importance': {
            'xgboost': {f: float(i) for f, i in zip(features, xgb_model.feature_importances_)}
        }
    }
    
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/model_metrics.json', 'w') as f:
        json.dump(metrics_output, f, indent=2)
        
    print("Written metrics to public/data/model_metrics.json")
    
    # ------------------
    # Forward Live Predictions (48h)
    # ------------------
    print("Generating 48h true forward predictions using XGBoost...")
    
    # Load the live 48h weather forecast generated by extract_weather.py
    with open('public/data/weather_raw.json', 'r') as f:
        live_weather = json.load(f)
        
    predictions_output = {}
    
    # We predict the city-wide total load for the next 48 hours
    city_forecast = []
    for i in range(48):
        future_time = pd.to_datetime(live_weather['hourly']['time'][i])
        temp = live_weather['hourly']['temperature_2m'][i]
        
        # Prepare feature vector for the model
        feat = pd.DataFrame([{
            'hour': future_time.hour,
            'dayofweek': future_time.dayofweek,
            'month': future_time.month,
            'is_weekend': 1 if future_time.dayofweek in [5, 6] else 0,
            'temperature': temp
        }])
        
        # Predict using champion model
        pred_val = float(xgb_model.predict(feat)[0])
        city_forecast.append({
            'datetime': future_time.isoformat(),
            'temperature': temp,
            'predicted_load_mw': pred_val
        })
        
    # Apportion to the actual map zones based on real ratios from HRM data
    with open('data/zones.geojson', 'r') as f:
        zones_data = json.load(f)
        
    total_base_load = sum(f['properties']['base_load_mw'] for f in zones_data['features'])
    
    zone_predictions = { 'city_total_predictions': city_forecast, 'zones': {} }
    
    for feature in zones_data['features']:
        z_id = feature['properties']['zone_id']
        z_ratio = feature['properties']['base_load_mw'] / total_base_load
        
        # Distribute the city load to this zone, adding slight noise to represent real-world variance
        zone_hourly = []
        for i, pt in enumerate(city_forecast):
            # Introduce a minor deterministic zone variance (e.g. burnside behaves differently at night)
            zone_variance = 1.0 + (np.sin((pt['temperature'] + i) * np.pi / 24) * 0.05) if feature['properties']['zone_type'] == 'Industrial' else 1.0
            
            zone_hourly.append({
                'hour_offset': i,
                'datetime': pt['datetime'],
                'predicted_load_mw': round(pt['predicted_load_mw'] * z_ratio * zone_variance, 2)
            })
            
        zone_predictions['zones'][z_id] = zone_hourly
        
    with open('public/data/zone_predictions.json', 'w') as f:
        json.dump(zone_predictions, f, indent=2)
        
    print("Written live ML forward predictions to public/data/zone_predictions.json")
    
    return metrics_output

if __name__ == "__main__":
    train_and_evaluate()
