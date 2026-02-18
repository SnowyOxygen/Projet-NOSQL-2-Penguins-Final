import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Part2.css';

function Part2() {
  const [variable, setVariable] = useState('body_mass_g');
  const [distributionData, setDistributionData] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const [scatterData, setScatterData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const variables = [
    { label: 'Body Mass (g)', value: 'body_mass_g' },
    { label: 'Bill Length (mm)', value: 'bill_length_mm' },
    { label: 'Bill Depth (mm)', value: 'bill_depth_mm' },
    { label: 'Flipper Length (mm)', value: 'flipper_length_mm' }
  ];

  useEffect(() => {
    fetchData();
  }, [variable]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [distRes, corrRes, scatterRes] = await Promise.all([
        axios.get(`/api/part2/distribution?variable=${variable}`),
        axios.get('/api/part2/correlation'),
        axios.get('/api/part2/scatter')
      ]);
      setDistributionData(distRes.data);
      setCorrelationData(corrRes.data);
      setScatterData(scatterRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load visualization data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading"></div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="part2-container">
      <h2>Part 2: Data Visualization</h2>

      <div className="section">
        <h3>Distribution Analysis</h3>
        <label htmlFor="variable-select">Select Variable:</label>
        <select 
          id="variable-select"
          value={variable} 
          onChange={(e) => setVariable(e.target.value)}
          className="variable-select"
        >
          {variables.map(v => (
            <option key={v.value} value={v.value}>{v.label}</option>
          ))}
        </select>

        {distributionData && (
          <div className="distribution-analysis">
            <div className="stats-box">
              <h4>Statistics</h4>
              <p><strong>Mean:</strong> {distributionData.mean?.toFixed(2)}</p>
              <p><strong>Std Dev:</strong> {distributionData.std?.toFixed(2)}</p>
              <p><strong>Count:</strong> {distributionData.count}</p>
            </div>

            <div className="quartiles-box">
              <h4>Quartiles</h4>
              <p><strong>Min:</strong> {distributionData.quartiles?.q0?.toFixed(2)}</p>
              <p><strong>Q1:</strong> {distributionData.quartiles?.q1?.toFixed(2)}</p>
              <p><strong>Median:</strong> {distributionData.quartiles?.q2?.toFixed(2)}</p>
              <p><strong>Q3:</strong> {distributionData.quartiles?.q3?.toFixed(2)}</p>
              <p><strong>Max:</strong> {distributionData.quartiles?.q4?.toFixed(2)}</p>
            </div>

            <div className="histogram">
              <h4>Histogram</h4>
              <div className="histogram-bars">
                {distributionData.histogram?.map((bin, idx) => {
                  const maxCount = Math.max(...distributionData.histogram.map(b => b.count));
                  const height = (bin.count / maxCount) * 100;
                  return (
                    <div key={idx} className="bar-container">
                      <div 
                        className="bar"
                        style={{ height: `${height}%` }}
                        title={`${bin.bin}: ${bin.count}`}
                      ></div>
                      <label>{bin.bin}</label>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="section">
        <h3>Correlation Matrix</h3>
        {correlationData && (
          <div className="correlation-heatmap">
            <table className="correlation-table">
              <thead>
                <tr>
                  <th></th>
                  {correlationData.variables?.map(v => (
                    <th key={v}>{v}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {correlationData.variables?.map((rowVar, rowIdx) => (
                  <tr key={rowIdx}>
                    <td><strong>{rowVar}</strong></td>
                    {correlationData.variables?.map((colVar, colIdx) => {
                      const value = correlationData.correlations[rowIdx][colIdx];
                      const intensity = Math.abs(value);
                      const color = value > 0 
                        ? `rgba(102, 126, 234, ${intensity})`
                        : `rgba(245, 87, 108, ${intensity})`;
                      return (
                        <td 
                          key={colIdx}
                          className="correlation-cell"
                          style={{ backgroundColor: color }}
                          title={`${value.toFixed(3)}`}
                        >
                          {value.toFixed(2)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="section">
        <h3>Scatter Plots - Relationship Analysis</h3>
        
        {scatterData && (
          <>
            <div className="scatter-plot-container">
              <h4>Bill Length vs Bill Depth (by Species)</h4>
              <svg className="scatter-plot" viewBox="0 0 500 400">
                {/* Axes */}
                <line x1="50" y1="350" x2="450" y2="350" stroke="#333" strokeWidth="2"/>
                <line x1="50" y1="350" x2="50" y2="50" stroke="#333" strokeWidth="2"/>
                
                {/* Axis labels */}
                <text x="250" y="390" textAnchor="middle" fontSize="14">Bill Length (mm)</text>
                <text x="20" y="200" textAnchor="middle" fontSize="14" transform="rotate(-90, 20, 200)">Bill Depth (mm)</text>
                
                {/* Data points */}
                {scatterData.bill_scatter?.map((point, idx) => {
                  const xMin = Math.min(...scatterData.bill_scatter.map(p => p.x));
                  const xMax = Math.max(...scatterData.bill_scatter.map(p => p.x));
                  const yMin = Math.min(...scatterData.bill_scatter.map(p => p.y));
                  const yMax = Math.max(...scatterData.bill_scatter.map(p => p.y));
                  
                  const x = 50 + ((point.x - xMin) / (xMax - xMin)) * 400;
                  const y = 350 - ((point.y - yMin) / (yMax - yMin)) * 300;
                  
                  const colors = {
                    'Adelie': '#FF6B6B',
                    'Chinstrap': '#4ECDC4',
                    'Gentoo': '#95E1D3'
                  };
                  
                  return (
                    <circle
                      key={idx}
                      cx={x}
                      cy={y}
                      r="4"
                      fill={colors[point.species] || '#999'}
                      opacity="0.6"
                    />
                  );
                })}
              </svg>
              <div className="scatter-legend">
                <span><span className="legend-dot" style={{backgroundColor: '#FF6B6B'}}></span> Adelie</span>
                <span><span className="legend-dot" style={{backgroundColor: '#4ECDC4'}}></span> Chinstrap</span>
                <span><span className="legend-dot" style={{backgroundColor: '#95E1D3'}}></span> Gentoo</span>
              </div>
            </div>

            <div className="scatter-plot-container">
              <h4>Flipper Length vs Body Mass (by Sex)</h4>
              <svg className="scatter-plot" viewBox="0 0 500 400">
                {/* Axes */}
                <line x1="50" y1="350" x2="450" y2="350" stroke="#333" strokeWidth="2"/>
                <line x1="50" y1="350" x2="50" y2="50" stroke="#333" strokeWidth="2"/>
                
                {/* Axis labels */}
                <text x="250" y="390" textAnchor="middle" fontSize="14">Flipper Length (mm)</text>
                <text x="20" y="200" textAnchor="middle" fontSize="14" transform="rotate(-90, 20, 200)">Body Mass (g)</text>
                
                {/* Data points */}
                {scatterData.flipper_scatter?.map((point, idx) => {
                  const xMin = Math.min(...scatterData.flipper_scatter.map(p => p.x));
                  const xMax = Math.max(...scatterData.flipper_scatter.map(p => p.x));
                  const yMin = Math.min(...scatterData.flipper_scatter.map(p => p.y));
                  const yMax = Math.max(...scatterData.flipper_scatter.map(p => p.y));
                  
                  const x = 50 + ((point.x - xMin) / (xMax - xMin)) * 400;
                  const y = 350 - ((point.y - yMin) / (yMax - yMin)) * 300;
                  
                  const colors = {
                    'MALE': '#667EEA',
                    'FEMALE': '#F56565'
                  };
                  
                  return (
                    <circle
                      key={idx}
                      cx={x}
                      cy={y}
                      r="4"
                      fill={colors[point.sex] || '#999'}
                      opacity="0.6"
                    />
                  );
                })}
              </svg>
              <div className="scatter-legend">
                <span><span className="legend-dot" style={{backgroundColor: '#667EEA'}}></span> Male</span>
                <span><span className="legend-dot" style={{backgroundColor: '#F56565'}}></span> Female</span>
              </div>
            </div>
          </>
        )}
      </div>

      <button className="refresh-btn" onClick={fetchData}>Refresh Data</button>
    </div>
  );
}

export default Part2;
