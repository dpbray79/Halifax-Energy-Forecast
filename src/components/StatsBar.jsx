import React from 'react'

const StatsBar = ({ totalLoad, peakZoneName, currentTemp, bestModel }) => {
  const stats = [
    { label: 'Total Load', value: `${totalLoad.toLocaleString()} MW`, color: '#2D6A6A' },
    { label: 'Peak Zone', value: peakZoneName || 'Burnside', color: '#534AB7' },
    { label: 'Current Temp', value: `${currentTemp}°C` || '4.2°C', color: '#6B6860' },
    { label: 'Best Model', value: bestModel || 'XGBoost', color: '#1D9E75' }
  ]

  return (
    <div style={styles.container}>
      {stats.map(stat => (
        <div key={stat.label} style={styles.stat}>
          <div style={styles.label}>{stat.label}</div>
          <div style={{ ...styles.value, color: stat.color }}>{stat.value}</div>
        </div>
      ))}
    </div>
  )
}

const styles = {
  container: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginBottom: '24px'
  },
  stat: {
    background: 'white',
    borderRadius: '12px',
    padding: '16px 20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
  },
  label: {
    fontSize: '12px',
    color: '#9C9A92',
    marginBottom: '4px'
  },
  value: {
    fontSize: '22px',
    fontWeight: '600'
  }
}

export default StatsBar
