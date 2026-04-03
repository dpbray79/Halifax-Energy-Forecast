"""
Halifax Energy Geo - Step 6: Extract GeoJSON from HRM Open Data
================================================================
Fetches building footprints, zoning boundaries, and neighbourhoods
from the Halifax Regional Municipality ArcGIS REST API.

Run: python step6_geo_extract.py

Output: 
  - data/buildings.geojson
  - data/zoning.geojson
  - data/neighbourhoods.geojson
"""

import requests
import json
import os
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

# HRM ArcGIS REST API endpoints
HRM_BASE_URL = "https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services"

ENDPOINTS = {
    'buildings': f"{HRM_BASE_URL}/Building_Footprints/FeatureServer/0/query",
    'zoning': f"{HRM_BASE_URL}/Zoning_Boundaries/FeatureServer/0/query",
    'neighbourhoods': f"{HRM_BASE_URL}/Neighbourhood_Boundaries/FeatureServer/0/query",
    'land_use': f"{HRM_BASE_URL}/Generalized_Land_Use/FeatureServer/0/query"
}

# Halifax Peninsula bounding box (approximate)
HALIFAX_BBOX = {
    'xmin': -63.62,
    'ymin': 44.62,
    'xmax': -63.54,
    'ymax': 44.68
}

OUTPUT_DIR = "data"

# ============================================================
# FETCH FUNCTIONS
# ============================================================

def fetch_geojson(endpoint, name, bbox=None, max_records=5000):
    """
    Fetch GeoJSON data from ArcGIS REST API
    """
    print(f"\n  Fetching {name}...")
    
    params = {
        'where': '1=1',
        'outFields': '*',
        'f': 'geojson',
        'returnGeometry': 'true',
        'resultRecordCount': max_records
    }
    
    # Add bounding box filter if provided
    if bbox:
        params['geometry'] = f"{bbox['xmin']},{bbox['ymin']},{bbox['xmax']},{bbox['ymax']}"
        params['geometryType'] = 'esriGeometryEnvelope'
        params['spatialRel'] = 'esriSpatialRelIntersects'
        params['inSR'] = '4326'
        params['outSR'] = '4326'
    
    try:
        response = requests.get(endpoint, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if 'features' in data:
            print(f"    ✓ Retrieved {len(data['features'])} features")
            return data
        else:
            print(f"    ⚠ No features found or error: {data.get('error', 'Unknown')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Request failed: {e}")
        return None

def save_geojson(data, filename):
    """Save GeoJSON data to file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    size_kb = os.path.getsize(filepath) / 1024
    print(f"    ✓ Saved to {filepath} ({size_kb:.1f} KB)")
    
    return filepath

# ============================================================
# ZONE AGGREGATION
# ============================================================

def create_zone_summary(buildings_data, zoning_data):
    """
    Create summary statistics for each zone
    """
    print("\n  Creating zone summary...")
    
    zones = {}
    
    if zoning_data and 'features' in zoning_data:
        for feature in zoning_data['features']:
            props = feature.get('properties', {})
            zone_name = props.get('ZONE_NAME', props.get('zone_name', 'Unknown'))
            zone_type = props.get('ZONE_TYPE', props.get('zone_type', 'Unknown'))
            
            if zone_name not in zones:
                zones[zone_name] = {
                    'name': zone_name,
                    'type': zone_type,
                    'feature_count': 0,
                    'building_count': 0,
                    'estimated_area_m2': 0
                }
            
            zones[zone_name]['feature_count'] += 1
    
    # Create summary file
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_zones': len(zones),
        'zones': list(zones.values())
    }
    
    filepath = os.path.join(OUTPUT_DIR, 'zone_summary.json')
    with open(filepath, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"    ✓ Created zone summary with {len(zones)} zones")
    
    return summary

# ============================================================
# DEMO DATA (Fallback)
# ============================================================

def create_demo_zones():
    """
    Create demo zone data if API is unavailable
    Based on real Halifax geography
    """
    print("\n  Creating demo zone data...")
    
    demo_zones = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "zone_id": "downtown",
                    "name": "Downtown Halifax",
                    "zone_type": "Commercial",
                    "building_area_m2": 2450000,
                    "commercial_pct": 68,
                    "residential_pct": 22,
                    "industrial_pct": 10,
                    "base_load_mw": 1850
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-63.575, 44.648],
                        [-63.568, 44.652],
                        [-63.562, 44.648],
                        [-63.565, 44.642],
                        [-63.572, 44.640],
                        [-63.575, 44.648]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "zone_id": "northEnd",
                    "name": "North End",
                    "zone_type": "Mixed Use",
                    "building_area_m2": 1820000,
                    "commercial_pct": 35,
                    "residential_pct": 58,
                    "industrial_pct": 7,
                    "base_load_mw": 1420
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-63.568, 44.658],
                        [-63.558, 44.662],
                        [-63.550, 44.658],
                        [-63.555, 44.652],
                        [-63.565, 44.652],
                        [-63.568, 44.658]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "zone_id": "southEnd",
                    "name": "South End",
                    "zone_type": "Residential",
                    "building_area_m2": 1650000,
                    "commercial_pct": 18,
                    "residential_pct": 78,
                    "industrial_pct": 4,
                    "base_load_mw": 1180
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-63.582, 44.640],
                        [-63.575, 44.640],
                        [-63.572, 44.632],
                        [-63.578, 44.625],
                        [-63.585, 44.630],
                        [-63.582, 44.640]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "zone_id": "dartmouth",
                    "name": "Dartmouth",
                    "zone_type": "Mixed Use",
                    "building_area_m2": 2100000,
                    "commercial_pct": 42,
                    "residential_pct": 48,
                    "industrial_pct": 10,
                    "base_load_mw": 1580
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-63.548, 44.658],
                        [-63.538, 44.660],
                        [-63.532, 44.652],
                        [-63.535, 44.642],
                        [-63.545, 44.640],
                        [-63.550, 44.648],
                        [-63.548, 44.658]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "zone_id": "burnside",
                    "name": "Burnside Industrial",
                    "zone_type": "Industrial",
                    "building_area_m2": 3200000,
                    "commercial_pct": 25,
                    "residential_pct": 5,
                    "industrial_pct": 70,
                    "base_load_mw": 2200
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-63.545, 44.672],
                        [-63.528, 44.675],
                        [-63.520, 44.668],
                        [-63.525, 44.660],
                        [-63.540, 44.658],
                        [-63.548, 44.665],
                        [-63.545, 44.672]
                    ]]
                }
            }
        ]
    }
    
    save_geojson(demo_zones, 'zones.geojson')
    
    return demo_zones

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("HALIFAX ENERGY GEO - DATA EXTRACTION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n  Output directory: {OUTPUT_DIR}/")
    
    results = {}
    
    # Try to fetch from HRM API
    print("\n  Attempting to fetch from HRM Open Data API...")
    
    for name, endpoint in ENDPOINTS.items():
        data = fetch_geojson(endpoint, name, HALIFAX_BBOX)
        
        if data:
            save_geojson(data, f'{name}.geojson')
            results[name] = len(data.get('features', []))
        else:
            results[name] = 0
    
    # If no data fetched, create demo data
    total_features = sum(results.values())
    
    if total_features == 0:
        print("\n  ⚠ Could not fetch from HRM API - creating demo data...")
        demo_data = create_demo_zones()
        results['demo_zones'] = len(demo_data['features'])
    else:
        # Create zone summary from fetched data
        buildings = None
        zoning = None
        
        if os.path.exists(os.path.join(OUTPUT_DIR, 'buildings.geojson')):
            with open(os.path.join(OUTPUT_DIR, 'buildings.geojson')) as f:
                buildings = json.load(f)
        
        if os.path.exists(os.path.join(OUTPUT_DIR, 'zoning.geojson')):
            with open(os.path.join(OUTPUT_DIR, 'zoning.geojson')) as f:
                zoning = json.load(f)
        
        create_zone_summary(buildings, zoning)
    
    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    
    for name, count in results.items():
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {name}: {count} features")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
