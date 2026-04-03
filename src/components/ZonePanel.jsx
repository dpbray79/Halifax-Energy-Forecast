import React from 'react'

const ZonePanel = ({ zone, currentLoad }) => {
  if (!zone) return null

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <div style={{ ...styles.dot, background: zone.color }} />
        <div>
          <h3 style={styles.name}>{zone.name}</h3>
          <span style={styles.type}>{zone.type}</span>
        </div>
      </div>
      
      <div style={styles.grid}>
        <div style={styles.stat}>
          <div style={{ ...styles.statVal, color: '#D85A30' }}>
            {currentLoad.toLocaleString()}
          </div>
          <div style={styles.statLabel}>Est. Load (MW)</div>
        </div>
        <div style={styles.stat}>
          <div style={{ ...styles.statVal, color: '#2D6A6A' }}>
            {zone.commercialPct}%
          </div>
          <div style={styles.statLabel}>Commercial</div>
        </div>
        <div style={styles.stat}>
          <div style={{ ...styles.statVal, color: '#1D9E75' }}>
            {zone.residentialPct}%
          </div>
          <div style={styles.statLabel}>Residential</div>
        </div>
        <div style={styles.stat}>
          <div style={{ ...styles.statVal, color: '#534AB7' }}>
            {zone.industrialPct}%
          </div>
          <div style={styles.statLabel}>Industrial</div>
        </div>
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
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '16px'
  },
  dot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%'
  },
  name: {
    margin: 0,
    fontSize: '16px',
    fontWeight: '600',
    color: '#2C2A25'
  },
  type: {
    fontSize: '12px',
    color: '#9C9A92'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '12px'
  },
  stat: {
    background: '#F8F6F3',
    padding: '12px',
    borderRadius: '10px',
    textAlign: 'center'
  },
  statVal: {
    fontSize: '20px',
    fontWeight: '600'
  },
  statLabel: {
    fontSize: '11px',
    color: '#9C9A92',
    marginTop: '2px'
  }
}

export default ZonePanel
