import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { getZoneLoad, getLoadColor } from '../data/dataLoader'

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapView = ({ zones, selectedZone, currentHour, playMode, onZoneSelect, formatHour }) => {
  const [geoData, setGeoData] = useState(null)

  useEffect(() => {
    fetch('/data/zones.geojson')
      .then(res => res.json())
      .then(data => setZonesId(data))
      .catch(err => console.error('Error loading GeoJSON:', err))
  }, [])

  const setZonesId = (data) => {
    // Ensure every feature has an id for consistent selection
    const updated = {
      ...data,
      features: data.features.map(f => ({
        ...f,
        id: f.id || f.properties.zone_id
      }))
    }
    setGeoData(updated)
  }

  const onEachFeature = (feature, layer) => {
    layer.on({
      click: () => onZoneSelect(feature.id)
    });
    const load = getZoneLoad(zones, feature.id, currentHour % 24, playMode === 'forecast')
    layer.bindTooltip(`${feature.properties.name}: ${load} MW`, { sticky: true });
  }

  const zoneStyle = (feature) => {
    const load = getZoneLoad(zones, feature.id, currentHour % 24, playMode === 'forecast')
    return {
      fillColor: getLoadColor(load),
      weight: selectedZone === feature.id ? 4 : 2,
      opacity: 1,
      color: selectedZone === feature.id ? '#2D6A6A' : '#B8B4AC',
      fillOpacity: 0.7
    };
  }

  return (
    <div style={styles.container}>
      <MapContainer 
        center={[44.6488, -63.5752]} 
        zoom={12} 
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {geoData && (
          <GeoJSON 
            key={currentHour + selectedZone} // Force style refresh on hour/selection change
            data={geoData} 
            style={zoneStyle} 
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
      
      {/* Time overlay */}
      <div style={styles.timeOverlay}>
        <div style={styles.timeMode}>
          {playMode === 'historical' ? 'Historical' : 'Forecast'}
        </div>
        <div style={styles.timeVal}>{formatHour(currentHour)}</div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    background: '#F0EDE8',
    borderRadius: '12px',
    height: '400px',
    position: 'relative',
    overflow: 'hidden',
    boxShadow: 'inset 0 0 10px rgba(0,0,0,0.1)'
  },
  timeOverlay: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    background: 'white',
    padding: '12px 16px',
    borderRadius: '10px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
    zIndex: 1000
  },
  timeMode: {
    fontSize: '11px',
    color: '#9C9A92',
    marginBottom: '2px'
  },
  timeVal: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#2C2A25'
  }
}

export default MapView
