import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Part4.css';

function Part4() {
  const [billLength, setBillLength] = useState(40);
  const [billDepth, setBillDepth] = useState(18);
  const [flipperLength, setFlipperLength] = useState(190);
  const [bodyMass, setBodyMass] = useState(3800);
  const [prediction, setPrediction] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [modelStats, setModelStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showComparison, setShowComparison] = useState(false);

  useEffect(() => {
    fetchModelInfo();
    fetchModelStats();
  }, []);

  const fetchModelInfo = async () => {
    try {
      const response = await axios.get('/api/part4/model-info');
      setModelInfo(response.data);
    } catch (err) {
      setError('Failed to load model info: ' + err.message);
    }
  };

  const fetchModelStats = async () => {
    try {
      const response = await axios.get('/api/part4/stats');
      setModelStats(response.data);
    } catch (err) {
      console.error('Failed to load model stats:', err);
    }
  };

  const handlePredict = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/part4/predict', {
        bill_length_mm: parseFloat(billLength),
        bill_depth_mm: parseFloat(billDepth),
        flipper_length_mm: parseFloat(flipperLength),
        body_mass_g: parseFloat(bodyMass)
      });
      setPrediction(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to make prediction: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    try {
      setLoading(true);
      await axios.post('/api/part4/retrain');
      setError(null);
      alert('All models retrained successfully!');
      fetchModelInfo();
      fetchModelStats();
    } catch (err) {
      setError('Failed to retrain models: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteModel = async (modelKey) => {
    if (window.confirm(`Are you sure you want to delete the ${modelKey.toUpperCase()} model?`)) {
      try {
        setLoading(true);
        await axios.delete(`/api/part4/model?model=${modelKey}`);
        setError(null);
        alert(`${modelKey.toUpperCase()} model deleted successfully!`);
        fetchModelStats();
        fetchModelInfo();
      } catch (err) {
        setError(`Failed to delete ${modelKey.toUpperCase()} model: ` + err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const getModelColor = (modelKey) => {
    const colors = { rf: '#667eea', knn: '#f093fb', dt: '#4facfe' };
    return colors[modelKey] || '#666';
  };

  const getModelEmoji = (modelKey) => {
    const emojis = { rf: '🌳', knn: '🎯', dt: '🌲' };
    return emojis[modelKey] || '🤖';
  };

  const renderModelCard = (modelKey, metrics) => {
    if (!metrics) return null;
    const displayName = modelKey === 'rf' ? 'Random Forest' : modelKey === 'knn' ? 'K-Nearest Neighbors' : 'Decision Tree';
    
    return (
      <div key={modelKey} className="model-column" style={{ borderTopColor: getModelColor(modelKey) }}>
        <h4>{getModelEmoji(modelKey)} {displayName}</h4>
        
        <div className="model-stats-box">
          {modelStats && modelStats[modelKey] && (
            <>
              <div className="stat-item">
                <label>Training Samples</label>
                <p>{modelStats[modelKey].trained_samples || 'N/A'}</p>
              </div>
              <div className="stat-item">
                <label>Last Trained</label>
                <p>{modelStats[modelKey].trained_date ? new Date(modelStats[modelKey].trained_date).toLocaleDateString() : 'Not trained'}</p>
              </div>
              <div className="stat-item">
                <label>Status</label>
                <p className="status-badge">{modelStats[modelKey].exists ? '✅ Persisted' : '⚠️ Memory'}</p>
              </div>
            </>
          )}
        </div>

        <div className="metrics-box">
          <div className="metric-row">
            <span className="metric-label">Accuracy</span>
            <span className="metric-value" style={{ color: getModelColor(modelKey) }}>
              {(metrics.accuracy * 100).toFixed(1)}%
            </span>
          </div>

          {Object.entries(metrics.precision).map(([species, val]) => (
            <div key={`precision-${species}`} className="metric-row">
              <span className="metric-label">Precision ({species})</span>
              <span className="metric-value">{(val * 100).toFixed(1)}%</span>
            </div>
          ))}

          {Object.entries(metrics.recall).map(([species, val]) => (
            <div key={`recall-${species}`} className="metric-row">
              <span className="metric-label">Recall ({species})</span>
              <span className="metric-value">{(val * 100).toFixed(1)}%</span>
            </div>
          ))}

          {Object.entries(metrics.f1_score).map(([species, val]) => (
            <div key={`f1-${species}`} className="metric-row">
              <span className="metric-label">F1 ({species})</span>
              <span className="metric-value">{(val * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        {/* Feature Importance for RF and DT */}
        {modelInfo?.feature_importances && modelInfo.feature_importances[modelKey] && (
          <div className="feature-importance-mini">
            <h5>Feature Importance</h5>
            {modelInfo.feature_importances[modelKey].map((feat, idx) => (
              <div key={idx} className="feature-bar-mini">
                <label>{feat.feature.split('_').pop()}</label>
                <div className="bar-bg-mini">
                  <div 
                    className="bar-fg-mini"
                    style={{ width: `${feat.importance * 100}%`, backgroundColor: getModelColor(modelKey) }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {modelKey === 'knn' && (
          <div className="knn-note">
            <p>K-NN doesn't have feature importance scores</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="part4-container">
      <h2>Part 4: Classification & Species Prediction</h2>

      <div className="prediction-section">
        <h3>🎯 Predict Penguin Species</h3>
        <p>Adjust the sliders to input penguin measurements and see predictions from all three models.</p>

        <div className="sliders-group">
          <div className="slider-container">
            <label>
              Bill Length (mm): <strong>{billLength}</strong>
            </label>
            <input
              type="range"
              min="30"
              max="60"
              step="0.5"
              value={billLength}
              onChange={(e) => setBillLength(e.target.value)}
              className="slider"
            />
          </div>

          <div className="slider-container">
            <label>
              Bill Depth (mm): <strong>{billDepth}</strong>
            </label>
            <input
              type="range"
              min="15"
              max="22"
              step="0.5"
              value={billDepth}
              onChange={(e) => setBillDepth(e.target.value)}
              className="slider"
            />
          </div>

          <div className="slider-container">
            <label>
              Flipper Length (mm): <strong>{flipperLength}</strong>
            </label>
            <input
              type="range"
              min="170"
              max="230"
              step="1"
              value={flipperLength}
              onChange={(e) => setFlipperLength(e.target.value)}
              className="slider"
            />
          </div>

          <div className="slider-container">
            <label>
              Body Mass (g): <strong>{bodyMass}</strong>
            </label>
            <input
              type="range"
              min="2700"
              max="6500"
              step="50"
              value={bodyMass}
              onChange={(e) => setBodyMass(e.target.value)}
              className="slider"
            />
          </div>
        </div>

        <button className="predict-btn" onClick={handlePredict} disabled={loading}>
          {loading ? 'Predicting...' : '🎯 Predict Species'}
        </button>

        {error && <div className="error-message">{error}</div>}

        {prediction && (
          <div className="prediction-result">
            <h3>✅ Prediction Result (Random Forest)</h3>
            <div className="predicted-species">
              <div className="species-badge">
                {prediction.predicted_species}
              </div>
              <p className="confidence">
                <strong>Confidence:</strong> {(prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>

            <div className="probabilities">
              <h4>Class Probabilities</h4>
              {Object.entries(prediction.probabilities).map(([species, prob]) => (
                <div key={species} className="probability-bar">
                  <label>{species}</label>
                  <div className="bar-background">
                    <div 
                      className="bar-fill"
                      style={{ width: `${prob * 100}%` }}
                    >
                      <span className="percentage">{(prob * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Model Comparison Section */}
      {modelInfo && modelInfo.metrics && (
        <div className="model-comparison-section">
          <div className="comparison-header">
            <h3>⚖️ Model Comparison</h3>
            <button 
              className="toggle-btn"
              onClick={() => setShowComparison(!showComparison)}
            >
              {showComparison ? '▼ Hide Details' : '▶ Show Details'}
            </button>
          </div>

          <div className="models-grid">
            {renderModelCard('rf', modelInfo.metrics.rf)}
            {renderModelCard('knn', modelInfo.metrics.knn)}
            {renderModelCard('dt', modelInfo.metrics.dt)}
          </div>

          {showComparison && (
            <div className="comparison-details">
              <h4>📊 Detailed Accuracy Comparison</h4>
              <div className="accuracy-comparison">
                {Object.entries(modelInfo.metrics).map(([modelKey, metrics]) => (
                  <div key={modelKey} className="accuracy-bar-item">
                    <label>{modelKey === 'rf' ? '🌳 Random Forest' : modelKey === 'knn' ? '🎯 K-NN' : '🌲 Decision Tree'}</label>
                    <div className="accuracy-bar-bg">
                      <div 
                        className="accuracy-bar-fill"
                        style={{ width: `${metrics.accuracy * 100}%`, backgroundColor: getModelColor(modelKey) }}
                      >
                        <span>{(metrics.accuracy * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <h4>🎯 Per-Class Performance</h4>
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Random Forest</th>
                    <th>K-NN</th>
                    <th>Decision Tree</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Overall Accuracy</strong></td>
                    <td style={{ color: '#667eea' }}>{(modelInfo.metrics.rf.accuracy * 100).toFixed(1)}%</td>
                    <td style={{ color: '#f093fb' }}>{(modelInfo.metrics.knn.accuracy * 100).toFixed(1)}%</td>
                    <td style={{ color: '#4facfe' }}>{(modelInfo.metrics.dt.accuracy * 100).toFixed(1)}%</td>
                  </tr>
                  {Object.keys(modelInfo.metrics.rf.precision).map(species => (
                    <tr key={species}>
                      <td><strong>Precision ({species})</strong></td>
                      <td>{(modelInfo.metrics.rf.precision[species] * 100).toFixed(1)}%</td>
                      <td>{(modelInfo.metrics.knn.precision[species] * 100).toFixed(1)}%</td>
                      <td>{(modelInfo.metrics.dt.precision[species] * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Model Management Section */}
      {modelStats && (
        <div className="model-management-section">
          <h3>🔧 Model Management</h3>
          <div className="management-actions">
            <button 
              className="action-btn retrain-btn" 
              onClick={handleRetrain}
              disabled={loading}
            >
              {loading ? '⏳ Retraining...' : '🔄 Retrain All Models'}
            </button>
            {Object.keys(modelStats).some(k => modelStats[k]?.exists) && (
              <button 
                className="action-btn delete-btn" 
                onClick={() => {
                  if (window.confirm('Delete all models?')) {
                    Promise.all(['rf', 'knn', 'dt'].map(k => handleDeleteModel(k)));
                  }
                }}
                disabled={loading}
              >
                🗑️ Delete All Models
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Part4;
