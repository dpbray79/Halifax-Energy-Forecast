import json
import os

def extract_energy():
    print("Extracting energy patterns and building data...")
    # For this version, we'll use the existing zones.geojson if it exists, or create a mock.
    source_path = os.path.join("data", "zones.geojson")
    
    if os.path.exists(source_path):
        with open(source_path, "r") as f:
            data = json.load(f)
    else:
        # Minimal mock if missing
        data = {"type": "FeatureCollection", "features": []}
        
    output_path = os.path.join("public/data", "energy_raw.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Energy raw data saved to {output_path}")
    return data

if __name__ == "__main__":
    extract_energy()
