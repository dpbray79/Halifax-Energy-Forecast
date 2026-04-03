import React, { useState, useEffect } from 'react'

const ModelArena = () => {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/data/model_metrics.json')
      .then(res => res.json())
      .then(data => {
        setMetrics(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load metrics:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading Model Arena metrics...</div>
  }

  if (!metrics) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#D85A30' }}>
        No model metrics available. Please run the ETL pipeline training step.
      </div>
    )
  }

  const { dataset_info, models, feature_importance } = metrics
  const sortedFeatures = Object.entries(feature_importance.xgboost)
    .sort((a, b) => b[1] - a[1])

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>Model Execution Arena</h2>
      <p style={{ color: '#6B6860', marginBottom: '24px' }}>
        Live evaluation of predictive models on historical synthetic load data. Last trained: {new Date(metrics.generated_at).toLocaleString()}
      </p>

      {/* Dataset Overview */}
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>Dataset Split (80/20 Time Series)</h3>
        <div style={styles.splitBarContainer}>
          <div style={{ ...styles.splitBar, width: '80%', background: '#2D6A6A' }}>
            Train Set ({dataset_info.train_samples} hrs)
          </div>
          <div style={{ ...styles.splitBar, width: '20%', background: '#5DCAA5', color: '#1B4D4D' }}>
            Test Set ({dataset_info.test_samples} hrs)
          </div>
        </div>
        <p style={{ fontSize: '12px', color: '#6B6860', marginTop: '12px' }}>
          Total Samples: {dataset_info.total_samples} hourly records | Target: {dataset_info.target}
        </p>
      </div>

      <div style={styles.row}>
        {/* Model Metrics */}
        <div style={{ ...styles.card, flex: 2 }}>
          <h3 style={styles.cardTitle}>Live Model Accuracy (Test Data)</h3>
          
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #EDE9E3' }}>
                <th style={{ padding: '12px 8px' }}>Model</th>
                <th style={{ padding: '12px 8px' }}>Test RMSE</th>
                <th style={{ padding: '12px 8px' }}>Train RMSE</th>
                <th style={{ padding: '12px 8px' }}>R² (Test)</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(models).map(([key, data]) => (
                <tr key={key} style={{ borderBottom: '1px solid #EDE9E3' }}>
                  <td style={{ padding: '16px 8px', textTransform: 'capitalize', fontWeight: 'bold' }}>
                    {key.replace('_', ' ')}
                    {key === 'xgboost' && <span style={styles.badge}>Champion</span>}
                  </td>
                  <td style={{ padding: '16px 8px', fontWeight: 'bold', color: data.test_rmse < 50 ? '#1D9E75' : '#D85A30' }}>
                    {data.test_rmse} MW
                  </td>
                  <td style={{ padding: '16px 8px', color: '#6B6860' }}>{data.train_rmse} MW</td>
                  <td style={{ padding: '16px 8px' }}>{data.test_r2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Feature Importance */}
        <div style={{ ...styles.card, flex: 1 }}>
          <h3 style={styles.cardTitle}>XGBoost Feature Importance</h3>
          <div style={{ marginTop: '16px' }}>
            {sortedFeatures.map(([feature, importance]) => (
              <div key={feature} style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ textTransform: 'capitalize' }}>{feature.replace('_', ' ')}</span>
                  <span>{(importance * 100).toFixed(1)}%</span>
                </div>
                <div style={{ width: '100%', height: '8px', background: '#EDE9E3', borderRadius: '4px' }}>
                  <div style={{ 
                    width: `${importance * 100}%`, 
                    height: '100%', 
                    background: '#D4A574', 
                    borderRadius: '4px' 
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    height: '100%',
    fontFamily: "'DM Sans', sans-serif"
  },
  header: {
    fontSize: '24px',
    margin: '0',
    color: '#2C2A25'
  },
  row: {
    display: 'flex',
    gap: '24px'
  },
  card: {
    background: 'white',
    borderRadius: '16px',
    padding: '24px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.06)'
  },
  cardTitle: {
    fontSize: '16px',
    marginTop: 0,
    marginBottom: '16px',
    color: '#2C2A25'
  },
  splitBarContainer: {
    display: 'flex',
    height: '40px',
    borderRadius: '8px',
    overflow: 'hidden',
    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
  },
  splitBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '14px',
    fontWeight: 'bold',
    transition: 'width 0.5s ease'
  },
  badge: {
    background: '#FDF8F3',
    color: '#D4A574',
    padding: '4px 8px',
    fontSize: '10px',
    borderRadius: '12px',
    marginLeft: '8px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  }
}

export default ModelArena
