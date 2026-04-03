import React from 'react'

const TimelineControls = ({
  currentHour,
  setCurrentHour,
  isPlaying,
  setIsPlaying,
  playMode,
  setPlayMode,
  playSpeed,
  setPlaySpeed,
  activeLayer,
  setActiveLayer
}) => {
  const maxHour = playMode === 'historical' ? 23 : 47
  const progress = (currentHour / maxHour) * 100

  return (
    <div style={styles.container}>
      {/* Mode Toggle */}
      <div style={styles.modeToggle}>
        <button
          onClick={() => setPlayMode('historical')}
          style={{
            ...styles.modeBtn,
            ...(playMode === 'historical' ? styles.modeBtnHistorical : {})
          }}
        >
          ◀ Historical (24h)
        </button>
        <button
          onClick={() => setPlayMode('forecast')}
          style={{
            ...styles.modeBtn,
            ...(playMode === 'forecast' ? styles.modeBtnForecast : {})
          }}
        >
          Forecast (48h) ▶
        </button>
      </div>

      {/* Play Controls */}
      <div style={styles.playRow}>
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          style={{
            ...styles.playBtn,
            background: isPlaying ? '#D85A30' : '#2D6A6A'
          }}
        >
          {isPlaying ? '⏸' : '▶'}
        </button>

        <div style={styles.sliderWrap}>
          <input
            type="range"
            min="0"
            max={maxHour}
            value={currentHour}
            onChange={(e) => setCurrentHour(parseInt(e.target.value))}
            style={{
              ...styles.slider,
              background: `linear-gradient(to right, #2D6A6A ${progress}%, #D4D0C8 ${progress}%)`
            }}
          />
          <div style={styles.sliderLabels}>
            <span>{playMode === 'historical' ? '12:00 AM' : 'Now'}</span>
            <span>{playMode === 'historical' ? '11:00 PM' : '+48h'}</span>
          </div>
        </div>

        <select
          value={playSpeed}
          onChange={(e) => setPlaySpeed(parseInt(e.target.value))}
          style={styles.speedSelect}
        >
          <option value={2000}>0.5x</option>
          <option value={1000}>1x</option>
          <option value={500}>2x</option>
          <option value={250}>4x</option>
        </select>
      </div>

      {/* Layer Toggle */}
      <div style={styles.layers}>
        {['load', 'temp', 'zones'].map(layer => (
          <button
            key={layer}
            onClick={() => setActiveLayer(layer)}
            style={{
              ...styles.layerBtn,
              ...(activeLayer === layer ? styles.layerBtnActive : {})
            }}
          >
            {layer === 'load' ? '⚡ Load' : layer === 'temp' ? '🌡 Temp' : '🏢 Zones'}
          </button>
        ))}
      </div>
    </div>
  )
}

const styles = {
  container: {
    marginTop: '20px',
    padding: '16px',
    background: '#F8F6F3',
    borderRadius: '12px'
  },
  modeToggle: {
    display: 'flex',
    justifyContent: 'center',
    gap: '8px',
    marginBottom: '16px'
  },
  modeBtn: {
    padding: '8px 20px',
    borderRadius: '20px',
    border: 'none',
    background: 'white',
    color: '#6B6860',
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  },
  modeBtnHistorical: {
    background: '#2D6A6A',
    color: 'white'
  },
  modeBtnForecast: {
    background: '#D4A574',
    color: 'white'
  },
  playRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  playBtn: {
    width: '44px',
    height: '44px',
    borderRadius: '50%',
    border: 'none',
    color: 'white',
    fontSize: '16px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
    transition: 'all 0.2s ease'
  },
  sliderWrap: {
    flex: 1
  },
  slider: {
    width: '100%',
    height: '8px',
    borderRadius: '4px',
    appearance: 'none',
    cursor: 'pointer',
    outline: 'none'
  },
  sliderLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '4px',
    fontSize: '10px',
    color: '#9C9A92'
  },
  speedSelect: {
    padding: '8px 12px',
    borderRadius: '8px',
    border: '1px solid #D4D0C8',
    background: 'white',
    fontSize: '12px',
    color: '#4A4840',
    cursor: 'pointer'
  },
  layers: {
    display: 'flex',
    justifyContent: 'center',
    gap: '8px',
    marginTop: '16px'
  },
  layerBtn: {
    padding: '6px 16px',
    borderRadius: '6px',
    border: '1px solid #D4D0C8',
    background: 'white',
    color: '#6B6860',
    fontSize: '12px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  },
  layerBtnActive: {
    border: '1px solid #2D6A6A',
    background: '#E8F4F2',
    color: '#2D6A6A'
  }
}

export default TimelineControls
