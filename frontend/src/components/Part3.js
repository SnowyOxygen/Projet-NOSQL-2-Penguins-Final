import React, { useState } from 'react';
import axios from 'axios';
import './Part3.css';

function Part3() {
  const [regressionType, setRegressionType] = useState('simple');
  const [predictor, setPredictor] = useState('flipper_length_mm');
  const [predictors, setPredictors] = useState(['flipper_length_mm', 'bill_length_mm']);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const availableVariables = [
    { label: 'Bill Length (mm)', value: 'bill_length_mm' },
    { label: 'Bill Depth (mm)', value: 'bill_depth_mm' },
    { label: 'Flipper Length (mm)', value: 'flipper_length_mm' },
    { label: 'Body Mass (g)', value: 'body_mass_g' }
  ];

  const handleSimpleRegression = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/part3/simple?predictor=${predictor}`);
      setResult(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to perform regression: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMultipleRegression = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/part3/multiple', {
        predictors: predictors
      });
      setResult(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to perform regression: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const togglePredictor = (value) => {
    if (predictors.includes(value)) {
      setPredictors(predictors.filter(p => p !== value));
    } else {
      setPredictors([...predictors, value]);
    }
  };

  return (
    <div className="part3-container">
      <h2>Part 3: Regression Analysis</h2>

      <div className="regression-type-selector">
        <label>
          <input
            type="radio"
            value="simple"
            checked={regressionType === 'simple'}
            onChange={(e) => setRegressionType(e.target.value)}
          />
          Simple Linear Regression
        </label>
        <label>
          <input
            type="radio"
            value="multiple"
            checked={regressionType === 'multiple'}
            onChange={(e) => setRegressionType(e.target.value)}
          />
          Multiple Linear Regression
        </label>
      </div>

      {regressionType === 'simple' ? (
        <div className="section">
          <h3>Simple Linear Regression</h3>
          <div className="form-group">
            <label htmlFor="predictor-select">Predictor Variable:</label>
            <select
              id="predictor-select"
              value={predictor}
              onChange={(e) => setPredictor(e.target.value)}
              className="select-input"
            >
              {availableVariables.map(v => (
                <option key={v.value} value={v.value}>{v.label}</option>
              ))}
            </select>
          </div>
          <button className="analyze-btn" onClick={handleSimpleRegression} disabled={loading}>
            {loading ? 'Analyzing...' : 'Perform Regression'}
          </button>
        </div>
      ) : (
        <div className="section">
          <h3>Multiple Linear Regression</h3>
          <label>Select Predictor Variables:</label>
          <div className="checkbox-group">
            {availableVariables.map(v => (
              <label key={v.value} className="checkbox">
                <input
                  type="checkbox"
                  checked={predictors.includes(v.value)}
                  onChange={() => togglePredictor(v.value)}
                />
                {v.label}
              </label>
            ))}
          </div>
          <button className="analyze-btn" onClick={handleMultipleRegression} disabled={loading || predictors.length === 0}>
            {loading ? 'Analyzing...' : 'Perform Regression'}
          </button>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className="results-section">
          <h3>Results</h3>
          
          <div className="result-cards">
            <div className="result-card">
              <h4>Model Performance</h4>
              <p><strong>R² Score:</strong> {result.r_squared?.toFixed(4)}</p>
              <p><strong>Residual Std:</strong> {result.residual_std?.toFixed(2)}</p>
              <p><strong>P-value:</strong> {result.p_value?.toFixed(4)}</p>
              <p><strong>Samples Used:</strong> {result.samples_used}</p>
            </div>

            {result.equation && (
              <div className="result-card">
                <h4>Regression Equation</h4>
                <p className="equation">{result.equation}</p>
              </div>
            )}

            {result.coefficient !== undefined && (
              <div className="result-card">
                <h4>Coefficients</h4>
                <p><strong>Intercept:</strong> {result.intercept?.toFixed(4)}</p>
                <p><strong>Coefficient:</strong> {result.coefficient?.toFixed(4)}</p>
              </div>
            )}

            {result.coefficients && (
              <div className="result-card">
                <h4>Coefficients</h4>
                <p><strong>Intercept:</strong> {result.intercept?.toFixed(4)}</p>
                {Object.entries(result.coefficients).map(([key, value]) => (
                  <p key={key}><strong>{key}:</strong> {value?.toFixed(4)}</p>
                ))}
              </div>
            )}
          </div>

          <div className="interpretation">
            <h3>Interpretation</h3>
            <ul>
              <li><strong>R² Score:</strong> Indicates the proportion of variance explained by the model. Higher is better (0-1).</li>
              <li><strong>P-value:</strong> Tests if the relationship is statistically significant. Lower values indicate stronger evidence.</li>
              <li><strong>Residual Std:</strong> Standard deviation of prediction errors. Lower is better.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default Part3;
