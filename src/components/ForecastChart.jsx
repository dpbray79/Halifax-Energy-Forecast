import React from 'react'
import { getZoneLoad } from '../data/dataLoader'

const ForecastChart = ({ zones, zone, zoneId, currentHour, playMode }) => {
  if (!zone || !zones) return null

  const hours = Array.from({ length: 48 }, (_, i) => i)
  const maxLoad = (zone.baseLoad || 2000) * 1.1
  const peakLoad = Math.round((zone.baseLoad || 2000) * 1.05)

  return (
    <div style={styles.card}>
      <h4 style={styles.title}>
        48h Forecast — {zone.name.split(' ')[0]}
      </h4>
      
      <div style={styles.chartContainer}>
        {hours.map(hour => {
          const load = getZoneLoad(zones, zoneId, hour % 24, true)
          const height = Math.max((load / maxLoad) * 100, 5)
          const isCurrent = hour === currentHour && playMode === 'forecast'
          
          return (
            <div
              key={hour}
              style={{
                ...styles.bar,
                height: `${height}%`,
                background: isCurrent 
                  ? '#D85A30' 
                  : hour < 24 
                    ? 'linear-gradient(to top, #2D6A6A, #5DCAA5)'
                    : 'linear-gradient(to top, #D4A574, #E8C9A8)',
                opacity: isCurrent ? 1 : 0.7
              }}
            />
          )
        })}
      </div>
      
      <div style={styles.labels}>
        <span>Now</span>
        <span>+24h</span>
        <span>+48h</span>
      </div>
      
      <div style={styles.peakNote}>
        <strong style={{ color: '#D4A574' }}>Peak forecast:</strong>{' '}
        {peakLoad.toLocaleString()} MW at 6:00 PM tomorrow
      </div>
    </div>
  )
}

const styles = {
  card: {
    background: 'white',
    borderRadius: '16px',
    padding: '20px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.06)'
  },
  title: {
    margin: '0 0 16px',
    fontSize: '14px',
    fontWeight: '600',
    color: '#2C2A25'
  },
  chartContainer: {
    display: 'flex',
    alignItems: 'flex-end',
    height: '80px',
    gap: '2px'
  },
  bar: {
    flex: 1,
    borderRadius: '2px 2px 0 0',
    transition: 'all 0.2s ease'
  },
  labels: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '8px',
    fontSize: '10px',
    color: '#9C9A92'
  },
  peakNote: {
    marginTop: '12px',
    padding: '10px',
    background: '#FDF8F3',
    borderRadius: '8px',
    fontSize: '12px',
    color: '#6B6860'
  }
}

export default ForecastChart
