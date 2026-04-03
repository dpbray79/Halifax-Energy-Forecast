import json
import os

def transform():
    print("Transforming data and preserving geometries...")
    
    weather_path = "public/data/weather_raw.json"
    energy_path = "public/data/energy_raw.json"
    
    if not os.path.exists(weather_path) or not os.path.exists(energy_path):
        print("Missing raw data files. Run extraction first.")
        return
    
    with open(weather_path, "r") as f:
        weather = json.load(f)
    with open(energy_path, "r") as f:
        energy = json.load(f)
        
    # Default patterns
    PATTERNS = {
        'Commercial': [0.45, 0.42, 0.40, 0.38, 0.40, 0.48, 0.62, 0.78, 0.92, 0.98, 1.0, 0.98, 0.95, 0.92, 0.88, 0.85, 0.82, 0.78, 0.72, 0.68, 0.62, 0.55, 0.50, 0.47],
        'Residential': [0.55, 0.50, 0.48, 0.45, 0.48, 0.58, 0.75, 0.70, 0.58, 0.52, 0.50, 0.52, 0.55, 0.52, 0.50, 0.58, 0.75, 0.92, 0.98, 0.95, 0.88, 0.78, 0.68, 0.60],
        'Industrial': [0.35, 0.32, 0.30, 0.30, 0.35, 0.55, 0.78, 0.92, 0.98, 1.0, 1.0, 0.98, 0.95, 0.95, 0.92, 0.88, 0.75, 0.55, 0.42, 0.38, 0.35, 0.35, 0.35, 0.35],
        'Mixed Use': [0.50, 0.47, 0.44, 0.42, 0.45, 0.55, 0.70, 0.75, 0.78, 0.80, 0.78, 0.75, 0.72, 0.70, 0.68, 0.72, 0.80, 0.88, 0.92, 0.88, 0.80, 0.70, 0.62, 0.55]
    }
    
    processed_zones = {}
    
    # We want to output a GeoJSON for the map AND a lookup for the sidebar
    geojson_out = {
        "type": "FeatureCollection",
        "features": []
    }

    for feature in energy.get('features', []):
        props = feature['properties']
        geom = feature['geometry']
        z_id = props['zone_id']
        z_type = props['zone_type']
        
        # Add to lookup
        processed_zones[z_id] = {
            'id': z_id,
            'name': props['name'],
            'type': z_type,
            'baseLoad': props['base_load_mw'],
            'hourlyPattern': PATTERNS.get(z_type, PATTERNS['Mixed Use']),
            'currentTemp': weather['current_weather']['temperature']
        }
        
        # Add to GeoJSON
        new_feature = {
            "type": "Feature",
            "id": z_id,
            "properties": {
                **props,
                "current_temp": weather['current_weather']['temperature']
            },
            "geometry": geom
        }
        geojson_out['features'].append(new_feature)
    
    # Save both
    with open("public/data/transformed_data.json", "w") as f:
        json.dump(processed_zones, f, indent=2)
        
    with open("public/data/zones.geojson", "w") as f:
        json.dump(geojson_out, f, indent=2)
        
    print(f"Transformed data saved.")
    return processed_zones

if __name__ == "__main__":
    transform()
