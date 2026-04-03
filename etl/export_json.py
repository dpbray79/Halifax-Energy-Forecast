import json
import os

def export_json():
    print("Exporting final JSON files to public/data...")
    
    transformed_path = "public/data/transformed_data.json"
    predictions_path = "data/zone_predictions.json" # Reusing old output for now, or could use predict.py
    
    if not os.path.exists(transformed_path):
        print("Missing transformed data. Run transform first.")
        return
        
    with open(transformed_path, "r") as f:
        zones = json.load(f)
        
    # Standardize output for React
    output = {
        "generated_at": "2026-03-30T14:00:00Z",
        "zones": zones
    }
    
    output_path = "public/data/zones.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
        
    print(f"Final zones.json saved to {output_path}")
    
    # Also export status
    status = {
        "last_run": "2026-03-30T10:15:00Z",
        "status": "success",
        "version": "2.0.0-cloud"
    }
    with open("public/data/etl_status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    print("ETL status saved to public/data/etl_status.json")

if __name__ == "__main__":
    export_json()
