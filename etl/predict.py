import json
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
from datetime import datetime

def train_and_evaluate():
    print("Training ML models for Halifax Energy Forecast...")
    
    # Generate 1 year of synthetic historical hourly data to train on
    # (Since actual NS Power data is private)
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", end="2025-12-31 23:00:00", freq="h")
    
    # Feature Engineering
    df = pd.DataFrame({'datetime': dates})
    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['month'] = df['datetime'].dt.month
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    
    # Synthetic weather
    # Colder in winter (months 1, 2, 12), warmer in summer (6, 7, 8)
    base_temp = 10 + 15 * np.sin((df['month'] - 4) * (np.pi / 6))
    df['temperature'] = base_temp + np.random.normal(0, 5, len(df))
    
    # Synthetic building load calculation
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
            'random_forest': rf_metrics
        },
        'feature_importance': {
            'xgboost': {f: float(i) for f, i in zip(features, xgb_model.feature_importances_)}
        }
    }
    
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/model_metrics.json', 'w') as f:
        json.dump(metrics_output, f, indent=2)
        
    print("Written metrics to public/data/model_metrics.json")
    return metrics_output

if __name__ == "__main__":
    train_and_evaluate()
