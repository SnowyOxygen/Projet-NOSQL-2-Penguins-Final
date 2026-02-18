import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Part1.css';

function Part1() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/part1/summary');
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load statistics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading"></div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!data) return <div>No data available</div>;

  return (
    <div className="part1-container">
      <h2>Part 1: Descriptive Statistical Analysis</h2>
      
      <div className="stat-card">
        <h3>Dataset Overview</h3>
        <p><strong>Total Penguins:</strong> {data.total_penguins}</p>
      </div>

      <div className="section">
        <h3>Numeric Statistics</h3>
        <table className="stats-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th>Mean</th>
              <th>Median</th>
              <th>Min</th>
              <th>Max</th>
              <th>Std Dev</th>
              <th>Count</th>
              <th>Missing</th>
            </tr>
          </thead>
          <tbody>
            {data.numeric_stats && data.numeric_stats.map((stat, idx) => (
              <tr key={idx}>
                <td>{stat.variable}</td>
                <td>{stat.mean ? stat.mean.toFixed(2) : 'N/A'}</td>
                <td>{stat.median ? stat.median.toFixed(2) : 'N/A'}</td>
                <td>{stat.min ? stat.min.toFixed(2) : 'N/A'}</td>
                <td>{stat.max ? stat.max.toFixed(2) : 'N/A'}</td>
                <td>{stat.std ? stat.std.toFixed(2) : 'N/A'}</td>
                <td>{stat.count}</td>
                <td>{stat.missing_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="section">
        <h3>Species Distribution</h3>
        <div className="distribution-grid">
          {data.species_counts && data.species_counts.map((item, idx) => (
            <div key={idx} className="dist-card">
              <h4>{item.species}</h4>
              <p className="dist-count">{item.count}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="section">
        <h3>Island Distribution</h3>
        <div className="distribution-grid">
          {data.island_counts && data.island_counts.map((item, idx) => (
            <div key={idx} className="dist-card">
              <h4>{item.island}</h4>
              <p className="dist-count">{item.count}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="section">
        <h3>Sex Distribution</h3>
        <div className="distribution-grid">
          {data.sex_counts && data.sex_counts.map((item, idx) => (
            <div key={idx} className="dist-card">
              <h4>{item.sex}</h4>
              <p className="dist-count">{item.count}</p>
            </div>
          ))}
        </div>
      </div>

      {Object.keys(data.missing_values || {}).length > 0 && (
        <div className="section">
          <h3>Missing Values</h3>
          <ul>
            {Object.entries(data.missing_values).map(([col, count], idx) => (
              <li key={idx}>{col}: {count} values</li>
            ))}
          </ul>
        </div>
      )}

      <button className="refresh-btn" onClick={fetchData}>Refresh Data</button>
    </div>
  );
}

export default Part1;
