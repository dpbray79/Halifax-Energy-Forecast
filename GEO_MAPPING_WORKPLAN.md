# Halifax Energy Forecaster — Geo-Mapping Integration Workplan

## Executive Summary

Integrate spatial visualization and zone-level predictions into the Halifax Energy dashboard. Since Nova Scotia Power doesn't provide public area-level consumption data, we'll use **proxy-based estimation** combining building footprints, land use zoning, population density, and weather patterns.

---

## Phase 1: Data Acquisition (Week 1)

### 1.1 HRM Open Data Hub
**Source:** https://data-hrm.hub.arcgis.com/

| Dataset | Format | Use Case |
|---------|--------|----------|
| Building Footprints | GeoJSON/Shapefile | Calculate total building area per zone |
| Zoning Boundaries | GeoJSON | Classify zones (R1, C1, M1, etc.) |
| Neighbourhoods | GeoJSON | User-friendly zone names |
| Land Use | GeoJSON | Commercial/Residential/Industrial mix |

**API Access:**
```
https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/
```

### 1.2 Statistics Canada Census Data
**Source:** CensusMapper API / Statistics Canada

| Dataset | Geography | Use Case |
|---------|-----------|----------|
| Dissemination Areas | 601 polygons in Halifax | Fine-grained spatial analysis |
| Dwelling Types | Per DA | Energy intensity by building type |
| Population Density | Per DA | Scale consumption estimates |
| Household Size | Per DA | Residential load factors |

**R Package:** `cancensus` (already familiar from NSCC courses)

### 1.3 Energy Intensity Benchmarks
**Source:** NRCan National Energy Use Database

| Building Type | Avg kWh/m²/year | Notes |
|---------------|-----------------|-------|
| Single-family residential | 150-200 | Nova Scotia avg |
| Multi-unit residential | 120-160 | Shared walls reduce load |
| Office/commercial | 200-350 | HVAC dominant |
| Retail | 250-400 | Lighting + HVAC |
| Industrial | 150-500 | Varies widely |

---

## Phase 2: Proxy Model Design (Week 2)

### 2.1 Energy Estimation Formula

```
Zone_Load_MW = Σ (Building_Area_m² × Intensity_kWh_m² × Weather_Factor × Hour_Factor) / 1000
```

**Components:**

1. **Building_Area_m²** — From HRM building footprints
2. **Intensity_kWh_m²** — Lookup by land use zone type
3. **Weather_Factor** — From your existing weather features:
   - HDD/CDD scaling
   - Temperature deviation from 18°C baseline
4. **Hour_Factor** — From your existing hourly patterns:
   - Commercial peaks 9am-5pm
   - Residential peaks 6pm-9pm

### 2.2 Zone Classification

Map HRM zoning codes to energy profiles:

| Zone Code | Category | Base Intensity | Peak Hour |
|-----------|----------|----------------|-----------|
| R-1, R-2 | Low-density residential | 150 kWh/m² | 7pm |
| R-3, R-4 | Medium-density residential | 130 kWh/m² | 7pm |
| C-1, C-2 | Commercial | 280 kWh/m² | 2pm |
| MU-1 | Mixed use | 200 kWh/m² | 5pm |
| I-1, I-2 | Industrial | 300 kWh/m² | 11am |

### 2.3 Database Schema Extensions

```sql
-- New tables for geo data
CREATE TABLE Geo_Zone (
    ZoneID INT IDENTITY PRIMARY KEY,
    ZoneName VARCHAR(100),
    ZoneType VARCHAR(50),
    GeometryJSON TEXT,
    TotalArea_m2 FLOAT,
    BuildingArea_m2 FLOAT,
    CommercialPct FLOAT,
    ResidentialPct FLOAT,
    IndustrialPct FLOAT,
    PopulationDensity FLOAT
);

CREATE TABLE Zone_Predictions (
    PredID INT IDENTITY PRIMARY KEY,
    ZoneID INT FOREIGN KEY REFERENCES Geo_Zone(ZoneID),
    DateTime DATETIME,
    Predicted_Load_MW FLOAT,
    Confidence_Upper FLOAT,
    Confidence_Lower FLOAT,
    ModelVersion VARCHAR(50),
    WeatherAdjustment FLOAT
);
```

---

## Phase 3: ETL Pipeline Extension (Week 3)

### 3.1 New ETL Steps

| Step | Script | Description |
|------|--------|-------------|
| Step 6 | `step6_geo_extract.py` | Fetch GeoJSON from HRM ArcGIS |
| Step 7 | `step7_geo_transform.py` | Calculate zone metrics, join census data |
| Step 8 | `step8_zone_predict.py` | Run models per zone |

### 3.2 step6_geo_extract.py (Pseudocode)

```python
import requests
import geopandas as gpd

# HRM ArcGIS REST endpoints
ENDPOINTS = {
    'buildings': 'https://services2.arcgis.com/.../Buildings/FeatureServer/0/query',
    'zoning': 'https://services2.arcgis.com/.../Zoning/FeatureServer/0/query',
    'neighbourhoods': 'https://services2.arcgis.com/.../Neighbourhoods/FeatureServer/0/query'
}

def fetch_geojson(endpoint, bbox=None):
    params = {
        'where': '1=1',
        'outFields': '*',
        'f': 'geojson',
        'geometry': bbox,  # Halifax peninsula bounds
        'geometryType': 'esriGeometryEnvelope'
    }
    response = requests.get(endpoint, params=params)
    return response.json()

def main():
    # Fetch all layers
    buildings = fetch_geojson(ENDPOINTS['buildings'])
    zoning = fetch_geojson(ENDPOINTS['zoning'])
    
    # Save to local GeoJSON
    with open('data/buildings.geojson', 'w') as f:
        json.dump(buildings, f)
    
    # Load into SQL Server
    gdf = gpd.read_file('data/buildings.geojson')
    # ... insert to Geo_Zone table
```

### 3.3 step8_zone_predict.py (Pseudocode)

```python
def predict_by_zone(zones, base_predictions):
    """
    Distribute city-wide predictions to zones based on:
    - Zone building area (proportion of city total)
    - Zone type (commercial peaks differently than residential)
    - Time of day adjustments
    """
    zone_predictions = []
    
    for zone in zones:
        # Get zone's share of total building area
        zone_share = zone.building_area / total_city_area
        
        # Apply zone-type adjustment
        if zone.type == 'commercial':
            hour_adjustment = commercial_curve[current_hour]
        elif zone.type == 'residential':
            hour_adjustment = residential_curve[current_hour]
        
        # Calculate zone prediction
        zone_load = base_prediction * zone_share * hour_adjustment
        
        zone_predictions.append({
            'zone_id': zone.id,
            'predicted_load': zone_load,
            'confidence': base_confidence * 1.1  # Wider band for zone-level
        })
    
    return zone_predictions
```

---

## Phase 4: React Dashboard Redesign (Week 4)

### 4.1 Tech Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Map rendering | react-map-gl (Mapbox) or react-leaflet | Interactive map |
| GeoJSON layers | deck.gl or leaflet-geojson | Choropleth overlays |
| Charts | Recharts (already planned) | Zone-level charts |
| State management | React Context | Selected zone, time slice |

### 4.2 Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Halifax Energy Forecaster          [Map] [Arena] [Lab] [Pipe] │
├────────────────────────────────────────────────────────────────┤
│                                           │                    │
│   ┌─────────────────────────────────┐    │  Selected Zone     │
│   │                                 │    │  ─────────────     │
│   │     Interactive Map             │    │  Downtown Core     │
│   │     (Choropleth by load)        │    │                    │
│   │                                 │    │  Est Load: 2,145MW │
│   │     [Click zones to select]     │    │  68% Commercial    │
│   │                                 │    │  Best: XGBoost     │
│   │                                 │    │                    │
│   └─────────────────────────────────┘    │  48h Forecast      │
│                                           │  ┌──────────────┐ │
│   Time: [═══════●═══════] 2:00 PM        │  │ ▁▃▅▇▅▃▁▃▅▇  │ │
│   Layer: [Load] [Temp] [Zones]           │  └──────────────┘ │
│                                           │                    │
└────────────────────────────────────────────────────────────────┘
```

### 4.3 Key Components

```jsx
// src/components/MapView.jsx
import Map, { Source, Layer } from 'react-map-gl';
import { useState } from 'react';

export function MapView({ zones, predictions, onZoneSelect }) {
  const [hoveredZone, setHoveredZone] = useState(null);
  
  // Color scale based on load intensity
  const getColor = (load) => {
    if (load > 2000) return '#D85A30';  // Coral - high
    if (load > 1500) return '#EF9F27';  // Amber - medium
    return '#5DCAA5';                    // Teal - low
  };
  
  return (
    <Map
      mapboxAccessToken={MAPBOX_TOKEN}
      initialViewState={{
        latitude: 44.6488,
        longitude: -63.5752,
        zoom: 12
      }}
      style={{ width: '100%', height: 400 }}
      mapStyle="mapbox://styles/mapbox/dark-v11"
    >
      <Source type="geojson" data={zones}>
        <Layer
          type="fill"
          paint={{
            'fill-color': ['get', 'color'],
            'fill-opacity': 0.7
          }}
          onClick={(e) => onZoneSelect(e.features[0])}
        />
      </Source>
    </Map>
  );
}
```

### 4.4 Data Flow

```
JSON files (from ETL)
    ↓
React App loads on mount
    ↓
MapView renders choropleth
    ↓
User clicks zone
    ↓
ZonePanel shows:
  - Zone stats
  - Model comparison for zone
  - 48h forecast for zone
    ↓
User adjusts time slider
    ↓
Map colors update to show
load patterns by hour
```

---

## Phase 5: Predictive Model Enhancement (Week 5)

### 5.1 Zone-Aware Features

Add to your feature set:

| Feature | Source | Rationale |
|---------|--------|-----------|
| `ZoneType` (one-hot) | HRM zoning | Different demand curves |
| `BuildingDensity` | HRM buildings / area | More buildings = more load |
| `CommercialRatio` | HRM land use | Commercial peaks midday |
| `ResidentialRatio` | HRM land use | Residential peaks evening |
| `PopulationDensity` | StatsCan | More people = more consumption |

### 5.2 Model Training Options

**Option A: Single model, zone as feature**
- Train one model with zone characteristics as features
- Simpler, but may miss zone-specific patterns

**Option B: Ensemble per zone type**
- Train separate models for Commercial, Residential, Industrial
- Better accuracy per zone, more complex

**Option C: Hierarchical model**
- Global model for city-wide prediction
- Zone-level model to distribute load
- Best of both worlds

**Recommendation:** Start with Option A, upgrade to C if accuracy suffers.

---

## Phase 6: Deployment (Week 6)

### 6.1 For Capstone Demo (VM)

1. Run ETL with geo steps
2. Export JSON including zone data
3. Serve React app locally (`npm run dev`)
4. Present Power BI + React side-by-side

### 6.2 For Portfolio (Cloud)

| Component | Service | Cost |
|-----------|---------|------|
| Database | Supabase (Postgres + PostGIS) | Free tier |
| ETL | GitHub Actions (scheduled) | Free |
| Frontend | Vercel | Free |
| Map tiles | Mapbox | Free tier (50k loads/mo) |

---

## Deliverables Checklist

### Data Layer
- [ ] HRM building footprints (GeoJSON)
- [ ] HRM zoning boundaries (GeoJSON)
- [ ] HRM neighbourhoods (GeoJSON)
- [ ] StatsCan dissemination areas (GeoJSON)
- [x] Energy intensity benchmarks (lookup table) ✅ Built into dashboard

### ETL Pipeline
- [ ] `step6_geo_extract.py`
- [ ] `step7_geo_transform.py`
- [ ] `step8_zone_predict.py`
- [ ] Updated `run_etl.py` with geo steps
- [ ] `zones.json` export for React

### Database
- [ ] `Geo_Zone` table
- [ ] `Zone_Predictions` table
- [ ] Spatial joins configured

### React Dashboard
- [x] MapView component (SVG-based Halifax zones) ✅ COMPLETE
- [x] ZonePanel component ✅ COMPLETE
- [x] Time slider with map update ✅ COMPLETE
- [x] Layer toggle (Load/Temp/Zones) ✅ COMPLETE
- [x] Responsive layout ✅ COMPLETE
- [x] Playable timeline — Historical mode (24h) ✅ COMPLETE
- [x] Playable timeline — Forecast mode (48h) ✅ COMPLETE
- [x] Play/Pause controls with speed adjustment ✅ COMPLETE
- [x] Dynamic zone coloring by load intensity ✅ COMPLETE
- [x] Zone selection with stats display ✅ COMPLETE
- [x] Model performance per zone ✅ COMPLETE
- [x] 48h forecast mini-chart ✅ COMPLETE
- [x] Light theme with earth tones ✅ COMPLETE

### Documentation
- [ ] README with setup instructions
- [ ] API documentation for JSON exports
- [ ] Methodology document for proxy estimation

---

## Completed Components (March 28, 2026)

### `HalifaxEnergyGeoDashboard.jsx`
Full React component with:
- Interactive SVG map of Halifax peninsula
- 5 zones: Downtown, North End, South End, Dartmouth, Burnside
- Playable timeline with Historical (24h) and Forecast (48h) modes
- Play/Pause with adjustable speed (0.5x, 1x, 2x, 4x)
- Zone click-to-select with detailed stats panel
- Model accuracy comparison per zone
- 48-hour forecast mini-chart
- Light theme with warm earth tones
- Responsive grid layout

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| HRM API rate limits | Cache GeoJSON locally, refresh weekly |
| No actual consumption data | Clearly label as "estimated" in UI |
| Map performance with many zones | Use vector tiles, simplify geometries |
| Mapbox token exposed | Use environment variables, domain restriction |

---

## Next Steps

1. **Today:** Confirm HRM ArcGIS endpoints are accessible
2. **This week:** Download initial GeoJSON files manually
3. **Next session:** Build `step6_geo_extract.py` and test
4. **Following:** Design zone prediction model

---

*Last updated: March 28, 2026*
*Project: NSCC Data Analytics Capstone*
*Author: Dylan Bray*
