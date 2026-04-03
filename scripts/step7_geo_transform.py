import json
import os

INPUT_FILE = "data/zones.geojson"
OUTPUT_FILE = "data/zones_processed.json"
JS_OUTPUT_FILE = "src/data/zones_dynamic.js"

# Default hourly patterns by zone type
PATTERNS = {
    'Commercial': [0.45, 0.42, 0.40, 0.38, 0.40, 0.48, 0.62, 0.78, 0.92, 0.98, 1.0, 0.98, 0.95, 0.92, 0.88, 0.85, 0.82, 0.78, 0.72, 0.68, 0.62, 0.55, 0.50, 0.47],
    'Residential': [0.55, 0.50, 0.48, 0.45, 0.48, 0.58, 0.75, 0.70, 0.58, 0.52, 0.50, 0.52, 0.55, 0.52, 0.50, 0.58, 0.75, 0.92, 0.98, 0.95, 0.88, 0.78, 0.68, 0.60],
    'Industrial': [0.35, 0.32, 0.30, 0.30, 0.35, 0.55, 0.78, 0.92, 0.98, 1.0, 1.0, 0.98, 0.95, 0.95, 0.92, 0.88, 0.75, 0.55, 0.42, 0.38, 0.35, 0.35, 0.35, 0.35],
    'Mixed Use': [0.50, 0.47, 0.44, 0.42, 0.45, 0.55, 0.70, 0.75, 0.78, 0.80, 0.78, 0.75, 0.72, 0.70, 0.68, 0.72, 0.80, 0.88, 0.92, 0.88, 0.80, 0.70, 0.62, 0.55]
}

COLORS = {
    'downtown': '#D85A30',
    'northEnd': '#EF9F27',
    'southEnd': '#1D9E75',
    'dartmouth': '#639922',
    'burnside': '#534AB7'
}

# Simplified SVG-like paths for the map (mocked from zones.js for demo purposes)
# In a real scenario, these would be generated from the geometry
PATHS = {
    'downtown': 'M180,130 L235,115 L270,130 L255,160 L200,168Z',
    'northEnd': 'M240,100 L310,85 L355,105 L335,140 L275,130Z',
    'southEnd': 'M140,145 L195,145 L210,185 L175,215 L130,195Z',
    'dartmouth': 'M360,110 L420,100 L455,130 L445,175 L395,188 L355,160Z',
    'burnside': 'M365,60 L430,52 L470,72 L465,105 L415,100 L360,82Z'
}

LABEL_POS = {
    'downtown': {'x': 220, 'y': 145},
    'northEnd': {'x': 295, 'y': 115},
    'southEnd': {'x': 165, 'y': 180},
    'dartmouth': {'x': 405, 'y': 148},
    'burnside': {'x': 415, 'y': 80}
}

def transform():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    processed_zones = {}

    for feature in data['features']:
        props = feature['properties']
        zone_id = props['zone_id']
        zone_type = props['zone_type']

        processed_zones[zone_id] = {
            'id': zone_id,
            'name': props['name'],
            'type': zone_type,
            'buildingArea': props['building_area_m2'],
            'commercialPct': props['commercial_pct'],
            'residentialPct': props['residential_pct'],
            'industrial_pct': props['industrial_pct'],
            'baseLoad': props['base_load_mw'],
            'hourlyPattern': PATTERNS.get(zone_type, PATTERNS['Mixed Use']),
            'color': COLORS.get(zone_id, '#999999'),
            'modelPerformance': { 'xgboost': 70 + (hash(zone_id) % 20), 'rf': 75 + (hash(zone_id) % 15), 'nn': 150 + (hash(zone_id) % 50) },
            'path': PATHS.get(zone_id, ''),
            'labelPos': LABEL_POS.get(zone_id, {'x': 0, 'y': 0})
        }

    # Save as JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(processed_zones, f, indent=2)
    print(f"Saved processed zones to {OUTPUT_FILE}")

    # Optionally generate a JS file for direct import if needed
    with open(JS_OUTPUT_FILE, 'w') as f:
        f.write("// Auto-generated from step7_geo_transform.py\n")
        f.write("export const zones = ")
        json.dump(processed_zones, f, indent=2)
        f.write("\n\n")
        f.write("// Utility functions (copied from original zones.js for compatibility)\n")
        f.write("export const getZoneLoad = (zoneId, hour, isForecast = false) => {\n")
        f.write("  const zone = zones[zoneId]\n")
        f.write("  if (!zone) return 0\n")
        f.write("  const basePattern = zone.hourlyPattern[hour % 24]\n")
        f.write("  const weatherFactor = 1 + (Math.sin(hour / 24 * Math.PI) * 0.1)\n")
        f.write("  const forecastUncertainty = isForecast ? (1 + (Math.random() - 0.5) * 0.05) : 1\n")
        f.write("  return Math.round(zone.baseLoad * basePattern * weatherFactor * forecastUncertainty)\n")
        f.write("}\n\n")
        f.write("export const getTotalLoad = (hour, isForecast = false) => {\n")
        f.write("  return Object.keys(zones).reduce((sum, zoneId) => {\n")
        f.write("    return sum + getZoneLoad(zoneId, hour, isForecast)\n")
        f.write("  }, 0)\n")
        f.write("}\n\n")
        f.write("export const getLoadColor = (load, maxLoad = 2500) => {\n")
        f.write("  const intensity = Math.min(load / maxLoad, 1)\n")
        f.write("  if (intensity > 0.75) return 'rgba(216, 90, 48, 0.8)'\n")
        f.write("  if (intensity > 0.5) return 'rgba(239, 159, 39, 0.7)'\n")
        f.write("  if (intensity > 0.25) return 'rgba(93, 202, 165, 0.6)'\n")
        f.write("  return 'rgba(133, 183, 235, 0.5)'\n")
        f.write("}\n\n")
        f.write("export const getBestModel = (zoneId) => {\n")
        f.write("  const zone = zones[zoneId]\n")
        f.write("  if (!zone) return 'XGBoost'\n")
        f.write("  const perf = zone.modelPerformance\n")
        f.write("  const min = Math.min(perf.xgboost, perf.rf, perf.nn)\n")
        f.write("  if (min === perf.xgboost) return 'XGBoost'\n")
        f.write("  if (min === perf.rf) return 'Random Forest'\n")
        f.write("  return 'Neural Network'\n")
        f.write("}\n")
    print(f"Saved dynamic patterns to {JS_OUTPUT_FILE}")

if __name__ == "__main__":
    transform()
