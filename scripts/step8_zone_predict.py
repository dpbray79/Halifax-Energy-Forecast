import json
import os
import random

ZONES_FILE = "data/zones_processed.json"
OUTPUT_FILE = "data/zone_predictions.json"

def predict():
    if not os.path.exists(ZONES_FILE):
        print(f"Error: {ZONES_FILE} not found. Run step7 first.")
        return

    with open(ZONES_FILE, 'r') as f:
        zones = json.load(f)

    # Calculate total city base load
    total_base_load = sum(z['baseLoad'] for z in zones.values())
    
    # Simulate a current city-wide load (e.g., 85% of total base capacity)
    city_load_mw = total_base_load * 0.85
    
    predictions = {}
    
    for zone_id, zone in zones.items():
        # Zone's share of the city load
        share = zone['baseLoad'] / total_base_load
        
        # Apply some random variation per zone
        zone_specific_factor = 1.0 + (random.random() - 0.5) * 0.1
        
        predicted_load = city_load_mw * share * zone_specific_factor
        
        predictions[zone_id] = {
            'predicted_load_mw': round(predicted_load, 2),
            'confidence_interval': [round(predicted_load * 0.95, 2), round(predicted_load * 1.05, 2)],
            'timestamp': "2026-03-30T14:00:00Z"
        }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"Saved zone predictions to {OUTPUT_FILE}")
    print(f"City Total Predicted: {round(sum(p['predicted_load_mw'] for p in predictions.values()), 2)} MW")

if __name__ == "__main__":
    predict()
