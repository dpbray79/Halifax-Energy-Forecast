// Auto-generated from step7_geo_transform.py
export const zones = {
  "downtown": {
    "id": "downtown",
    "name": "Downtown Halifax",
    "type": "Commercial",
    "buildingArea": 2450000,
    "commercialPct": 68,
    "residentialPct": 22,
    "industrial_pct": 10,
    "baseLoad": 1850,
    "hourlyPattern": [
      0.45,
      0.42,
      0.4,
      0.38,
      0.4,
      0.48,
      0.62,
      0.78,
      0.92,
      0.98,
      1.0,
      0.98,
      0.95,
      0.92,
      0.88,
      0.85,
      0.82,
      0.78,
      0.72,
      0.68,
      0.62,
      0.55,
      0.5,
      0.47
    ],
    "color": "#D85A30",
    "modelPerformance": {
      "xgboost": 82,
      "rf": 82,
      "nn": 182
    },
    "path": "M180,130 L235,115 L270,130 L255,160 L200,168Z",
    "labelPos": {
      "x": 220,
      "y": 145
    }
  },
  "northEnd": {
    "id": "northEnd",
    "name": "North End",
    "type": "Mixed Use",
    "buildingArea": 1820000,
    "commercialPct": 35,
    "residentialPct": 58,
    "industrial_pct": 7,
    "baseLoad": 1420,
    "hourlyPattern": [
      0.5,
      0.47,
      0.44,
      0.42,
      0.45,
      0.55,
      0.7,
      0.75,
      0.78,
      0.8,
      0.78,
      0.75,
      0.72,
      0.7,
      0.68,
      0.72,
      0.8,
      0.88,
      0.92,
      0.88,
      0.8,
      0.7,
      0.62,
      0.55
    ],
    "color": "#EF9F27",
    "modelPerformance": {
      "xgboost": 80,
      "rf": 75,
      "nn": 190
    },
    "path": "M240,100 L310,85 L355,105 L335,140 L275,130Z",
    "labelPos": {
      "x": 295,
      "y": 115
    }
  },
  "southEnd": {
    "id": "southEnd",
    "name": "South End",
    "type": "Residential",
    "buildingArea": 1650000,
    "commercialPct": 18,
    "residentialPct": 78,
    "industrial_pct": 4,
    "baseLoad": 1180,
    "hourlyPattern": [
      0.55,
      0.5,
      0.48,
      0.45,
      0.48,
      0.58,
      0.75,
      0.7,
      0.58,
      0.52,
      0.5,
      0.52,
      0.55,
      0.52,
      0.5,
      0.58,
      0.75,
      0.92,
      0.98,
      0.95,
      0.88,
      0.78,
      0.68,
      0.6
    ],
    "color": "#1D9E75",
    "modelPerformance": {
      "xgboost": 87,
      "rf": 82,
      "nn": 197
    },
    "path": "M140,145 L195,145 L210,185 L175,215 L130,195Z",
    "labelPos": {
      "x": 165,
      "y": 180
    }
  },
  "dartmouth": {
    "id": "dartmouth",
    "name": "Dartmouth",
    "type": "Mixed Use",
    "buildingArea": 2100000,
    "commercialPct": 42,
    "residentialPct": 48,
    "industrial_pct": 10,
    "baseLoad": 1580,
    "hourlyPattern": [
      0.5,
      0.47,
      0.44,
      0.42,
      0.45,
      0.55,
      0.7,
      0.75,
      0.78,
      0.8,
      0.78,
      0.75,
      0.72,
      0.7,
      0.68,
      0.72,
      0.8,
      0.88,
      0.92,
      0.88,
      0.8,
      0.7,
      0.62,
      0.55
    ],
    "color": "#639922",
    "modelPerformance": {
      "xgboost": 88,
      "rf": 88,
      "nn": 158
    },
    "path": "M360,110 L420,100 L455,130 L445,175 L395,188 L355,160Z",
    "labelPos": {
      "x": 405,
      "y": 148
    }
  },
  "burnside": {
    "id": "burnside",
    "name": "Burnside Industrial",
    "type": "Industrial",
    "buildingArea": 3200000,
    "commercialPct": 25,
    "residentialPct": 5,
    "industrial_pct": 70,
    "baseLoad": 2200,
    "hourlyPattern": [
      0.35,
      0.32,
      0.3,
      0.3,
      0.35,
      0.55,
      0.78,
      0.92,
      0.98,
      1.0,
      1.0,
      0.98,
      0.95,
      0.95,
      0.92,
      0.88,
      0.75,
      0.55,
      0.42,
      0.38,
      0.35,
      0.35,
      0.35,
      0.35
    ],
    "color": "#534AB7",
    "modelPerformance": {
      "xgboost": 81,
      "rf": 86,
      "nn": 151
    },
    "path": "M365,60 L430,52 L470,72 L465,105 L415,100 L360,82Z",
    "labelPos": {
      "x": 415,
      "y": 80
    }
  }
}

// Utility functions (copied from original zones.js for compatibility)
export const getZoneLoad = (zoneId, hour, isForecast = false) => {
  const zone = zones[zoneId]
  if (!zone) return 0
  const basePattern = zone.hourlyPattern[hour % 24]
  const weatherFactor = 1 + (Math.sin(hour / 24 * Math.PI) * 0.1)
  const forecastUncertainty = isForecast ? (1 + (Math.random() - 0.5) * 0.05) : 1
  return Math.round(zone.baseLoad * basePattern * weatherFactor * forecastUncertainty)
}

export const getTotalLoad = (hour, isForecast = false) => {
  return Object.keys(zones).reduce((sum, zoneId) => {
    return sum + getZoneLoad(zoneId, hour, isForecast)
  }, 0)
}

export const getLoadColor = (load, maxLoad = 2500) => {
  const intensity = Math.min(load / maxLoad, 1)
  if (intensity > 0.75) return 'rgba(216, 90, 48, 0.8)'
  if (intensity > 0.5) return 'rgba(239, 159, 39, 0.7)'
  if (intensity > 0.25) return 'rgba(93, 202, 165, 0.6)'
  return 'rgba(133, 183, 235, 0.5)'
}

export const getBestModel = (zoneId) => {
  const zone = zones[zoneId]
  if (!zone) return 'XGBoost'
  const perf = zone.modelPerformance
  const min = Math.min(perf.xgboost, perf.rf, perf.nn)
  if (min === perf.xgboost) return 'XGBoost'
  if (min === perf.rf) return 'Random Forest'
  return 'Neural Network'
}
