import React, { useState, useEffect, useCallback } from 'react'
import MapView from './MapView'
import ZonePanel from './ZonePanel'
import TimelineControls from './TimelineControls'
import StatsBar from './StatsBar'
import ForecastChart from './ForecastChart'
import ModelComparison from './ModelComparison'
import ModelArena from './ModelArena'
import { loadZonesData, loadPredictionsData, getZoneLoad, getTotalLoad } from '../data/dataLoader'

const HalifaxEnergyGeoDashboard = () => {
  const [zones, setZones] = useState(null)
  const [predictions, setPredictions] = useState(null)
  const [currentHour, setCurrentHour] = useState(14)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playMode, setPlayMode] = useState('historical')
  const [selectedZone, setSelectedZone] = useState('downtown')
  const [activeLayer, setActiveLayer] = useState('load')
  const [playSpeed, setPlaySpeed] = useState(1000)
  const [activeTab, setActiveTab] = useState('map')

  // Load zones on mount
  useEffect(() => {
    Promise.all([loadZonesData(), loadPredictionsData()]).then(([zData, pData]) => {
      if (zData) setZones(zData)
      if (pData) setPredictions(pData)
    })
  }, [])

  // Playback logic
  useEffect(() => {
    let interval
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentHour(prev => {
          const max = playMode === 'historical' ? 23 : 47
          return prev >= max ? 0 : prev + 1
        })
      }, playSpeed)
    }
    return () => clearInterval(interval)
  }, [isPlaying, playMode, playSpeed])

  const handleModeChange = (mode) => {
    setPlayMode(mode)
    setCurrentHour(mode === 'historical' ? 14 : 0)
    setIsPlaying(false)
  }

  if (!zones || !predictions) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#F8F6F3' }}>Loading Geo-Mapping Data & ML Models...</div>
  }

  const zone = zones[selectedZone]
  const renderHour = playMode === 'forecast' ? currentHour : currentHour % 24
  const currentLoad = getZoneLoad(predictions, selectedZone, renderHour)
  const totalLoad = getTotalLoad(predictions, renderHour)
  const currentTemp = predictions.city_total_predictions[renderHour]?.temperature || 4.2
  
  // Find peak zone for StatsBar
  const peakZoneId = Object.keys(zones).reduce((a, b) => 
    getZoneLoad(predictions, a, renderHour) > getZoneLoad(predictions, b, renderHour) ? a : b
  )
  const peakZoneName = zones[peakZoneId].name.split(' ')[0]

  const formatHour = (h) => {
    const baseDate = new Date()
    baseDate.setHours(0, 0, 0, 0) // Start at midnight today
    baseDate.setHours(h) // Adding h hours automatically rolls over to the next day if h >= 24
    
    return baseDate.toLocaleString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric', 
      hour: 'numeric', 
      minute: '2-digit', 
      hour12: true 
    })
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Halifax Energy Forecaster</h1>
          <p style={styles.subtitle}>Real-time demand visualization & predictions</p>
        </div>
        <nav style={styles.nav}>
          {['map', 'arena', 'features', 'pipeline'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                ...styles.navBtn,
                ...(activeTab === tab ? styles.navBtnActive : {})
              }}
            >
              {tab === 'map' ? 'Map View' : 
               tab === 'arena' ? 'Model Arena' : 
               tab === 'features' ? 'Feature Lab' : 'Pipeline'}
            </button>
          ))}
        </nav>
      </header>

      {/* Stats Bar */}
      <StatsBar 
        totalLoad={totalLoad} 
        peakZoneName={peakZoneName} 
        currentTemp={currentTemp}
        bestModel="XGBoost"
      />

      {/* Main Content */}
      {activeTab === 'arena' ? (
        <main>
          <ModelArena />
        </main>
      ) : (
        <main style={styles.main}>
          {/* Map Area */}
          <div style={styles.mapCard}>
            <MapView
              zones={zones}
              selectedZone={selectedZone}
              currentHour={currentHour}
              playMode={playMode}
              onZoneSelect={setSelectedZone}
              formatHour={formatHour}
            />
            
            <TimelineControls
              currentHour={currentHour}
              setCurrentHour={setCurrentHour}
              isPlaying={isPlaying}
              setIsPlaying={setIsPlaying}
              playMode={playMode}
              setPlayMode={handleModeChange}
              playSpeed={playSpeed}
              setPlaySpeed={setPlaySpeed}
              activeLayer={activeLayer}
              setActiveLayer={setActiveLayer}
            />
          </div>

          {/* Sidebar */}
          <aside style={styles.sidebar}>
            <ZonePanel 
              zone={zone} 
              currentLoad={currentLoad}
            />
            
            <ModelComparison 
              zones={zones}
              zoneId={selectedZone}
            />
            
            <ForecastChart 
              zones={zones}
              predictions={predictions}
              zone={zone}
              zoneId={selectedZone}
              currentHour={currentHour}
              playMode={playMode}
            />
          </aside>
        </main>
      )}

      {/* Footer */}
      <footer style={styles.footer}>
        <span>Data: HRM Open Data • Statistics Canada • Open-Meteo</span>
        <span>NSCC Data Analytics Capstone — Dylan Bray</span>
      </footer>
    </div>
  )
}

const styles = {
  container: {
    fontFamily: "'DM Sans', sans-serif",
    background: 'linear-gradient(135deg, #F8F6F3 0%, #EDE9E3 100%)',
    minHeight: '100vh',
    padding: '24px'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  },
  title: {
    fontSize: '28px',
    fontWeight: '600',
    color: '#2C2A25',
    margin: 0,
    letterSpacing: '-0.5px'
  },
  subtitle: {
    fontSize: '14px',
    color: '#6B6860',
    margin: '4px 0 0'
  },
  nav: {
    display: 'flex',
    gap: '8px'
  },
  navBtn: {
    padding: '10px 20px',
    borderRadius: '8px',
    border: 'none',
    background: 'white',
    color: '#6B6860',
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
    transition: 'all 0.2s ease'
  },
  navBtnActive: {
    background: '#2D6A6A',
    color: 'white',
    boxShadow: '0 2px 8px rgba(45, 106, 106, 0.3)'
  },
  main: {
    display: 'grid',
    gridTemplateColumns: '1fr 360px',
    gap: '24px'
  },
  mapCard: {
    background: 'white',
    borderRadius: '16px',
    padding: '20px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.06)'
  },
  sidebar: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px'
  },
  footer: {
    marginTop: '24px',
    padding: '16px 20px',
    background: 'white',
    borderRadius: '12px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
    fontSize: '12px',
    color: '#9C9A92'
  }
}

export default HalifaxEnergyGeoDashboard
