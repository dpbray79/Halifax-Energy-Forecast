# Halifax Energy Geo Dashboard

Interactive energy demand forecasting dashboard with geo-mapping for Halifax, Nova Scotia.

![Dashboard Preview](docs/preview.png)

## Features

- **Interactive Map**: Click zones to see detailed stats
- **Playable Timeline**: Historical (24h) and Forecast (48h) modes
- **Model Comparison**: XGBoost, Random Forest, Neural Network per zone
- **Real-time Updates**: Watch load patterns change throughout the day
- **Light Theme**: Clean, professional earth-tone design

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+ (for geo extraction scripts)

### Installation

```bash
# Clone or download
cd HalifaxEnergyGeo

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
HalifaxEnergyGeo/
├── public/
├── src/
│   ├── components/
│   │   ├── HalifaxEnergyGeoDashboard.jsx  # Main dashboard
│   │   ├── MapView.jsx                     # SVG map
│   │   ├── ZonePanel.jsx                   # Zone details
│   │   ├── TimelineControls.jsx            # Play/pause, slider
│   │   ├── StatsBar.jsx                    # Top metrics
│   │   ├── ModelComparison.jsx             # ML model stats
│   │   └── ForecastChart.jsx               # 48h mini-chart
│   ├── data/
│   │   └── zones.js                        # Zone definitions
│   ├── App.jsx
│   └── main.jsx
├── scripts/
│   └── step6_geo_extract.py                # HRM data fetcher
├── package.json
└── vite.config.js
```

## Zones

| Zone | Type | Base Load | Peak Hour |
|------|------|-----------|-----------|
| Downtown Halifax | Commercial | 1,850 MW | 10 AM |
| North End | Mixed Use | 1,420 MW | 6 PM |
| South End | Residential | 1,180 MW | 7 PM |
| Dartmouth | Mixed Use | 1,580 MW | 6 PM |
| Burnside Industrial | Industrial | 2,200 MW | 10 AM |

## Data Sources

- **HRM Open Data**: Building footprints, zoning boundaries
- **Statistics Canada**: Population by dissemination area
- **Open-Meteo**: Historical and forecast weather
- **NRCan**: Energy intensity benchmarks

## Deployment

### Vercel (Recommended)

```bash
npm run build
npx vercel --prod
```

### GitHub Pages

```bash
npm run build
# Copy dist/ to gh-pages branch
```

## Related Files

This dashboard connects to the Halifax Energy ETL pipeline:

- `step2_extract.py` - Energy + weather data
- `step3_transform.py` - Feature engineering  
- `step4_export.py` - JSON for dashboard
- `step5_predict.py` - ML model predictions
- `step6_geo_extract.py` - GeoJSON zones

## Author

**Dylan Bray**  
NSCC Data Analytics Capstone 2026

## License

MIT
