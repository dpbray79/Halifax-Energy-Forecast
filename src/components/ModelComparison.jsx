import React from 'react'

const ModelComparison = ({ zones, zoneId }) => {
  const zone = zones[zoneId]
  if (!zone) return null

  // Use model performance from zone data or default mock
  const perf = zone.modelPerformance || { xgboost: 72.4, rf: 78.1, nn: 156.2 }
  const bestRmse = Math.min(perf.xgboost, perf.rf, perf.nn)

  const models = [
    { name: 'XGBoost', rmse: perf.xgboost, isBest: perf.xgboost === bestRmse },
    { name: 'Random Forest', rmse: perf.rf, isBest: perf.rf === bestRmse },
    { name: 'Neural Network', rmse: perf.nn, isBest: perf.nn === bestRmse }
  ]

  return (
    <div style={styles.card}>
      <h4 style={styles.title}>Model Accuracy (This Zone)</h4>
      
      {models.map(model => (
        <div key={model.name} style={styles.row}>
          <span style={styles.modelName}>{model.name}</span>
          <span style={{
            ...styles.rmse,
            color: model.isBest ? '#1D9E75' : model.rmse > 150 ? '#D85A30' : '#4A4840'
          }}>
            RMSE: {model.rmse}
            {model.isBest && <span style={styles.star}> ★ Best</span>}
          </span>
        </div>
      ))}
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
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 0',
    borderBottom: '1px solid #F0EDE8'
  },
  modelName: {
    fontSize: '13px',
    color: '#4A4840'
  },
  rmse: {
    fontSize: '13px',
    fontWeight: '600'
  },
  star: {
    fontSize: '10px',
    marginLeft: '4px'
  }
}

export default ModelComparison
