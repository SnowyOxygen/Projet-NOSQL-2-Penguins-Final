import React, { useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import './Part5.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function Part5() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('avg_time');

  const runBenchmark = async (database) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`/api/benchmark/${database}`);
      // Normalize single database result to match 'all' format
      const data = response.data;
      const normalizedData = {
        benchmarks: {
          [data.database.toLowerCase()]: data.metrics
        },
        detailed_results: {
          [data.database.toLowerCase()]: data.detailed_results
        },
        timestamp: data.timestamp
      };
      setResults(normalizedData);
    } catch (err) {
      setError(`Failed to run benchmark: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const runAllBenchmarks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('/api/benchmark/all');
      setResults(response.data);
    } catch (err) {
      setError(`Failed to run benchmarks: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getChartData = () => {
    if (!results || !results.benchmarks) {
      return null;
    }

    const databases = Object.keys(results.benchmarks);
    const metric = selectedMetric;

    return {
      labels: databases,
      datasets: [
        {
          label: metric === 'avg_time' ? 'Average Time (ms)' : 'Operations/second',
          data: databases.map(db => results.benchmarks[db][metric]),
          backgroundColor: [
            'rgba(75, 192, 192, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(255, 99, 132, 0.7)',
          ],
          borderColor: [
            'rgba(75, 192, 192, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(255, 99, 132, 1)',
          ],
          borderWidth: 2,
        },
      ],
    };
  };

  const getLineChartData = () => {
    if (!results || !results.detailed_results || !results.benchmarks) {
      return null;
    }

    const databases = Object.keys(results.benchmarks);
    if (databases.length === 0) return null;
    
    const testNumbers = results.detailed_results[databases[0]]?.map((_, i) => `Test ${i + 1}`) || [];

    return {
      labels: testNumbers,
      datasets: databases.map((db, idx) => ({
        label: db,
        data: results.detailed_results[db]?.map(r => r.time) || [],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 159, 64, 1)', 'rgba(255, 99, 132, 1)'][idx],
        backgroundColor: ['rgba(75, 192, 192, 0.1)', 'rgba(255, 159, 64, 0.1)', 'rgba(255, 99, 132, 0.1)'][idx],
        tension: 0.4,
      })),
    };
  };

  const chartData = getChartData();
  const lineChartData = getLineChartData();

  return (
    <div className="part5-container">
      <h2>⚡ Partie Annexe: Database Benchmarking</h2>
      <p className="subtitle">Compare performance across MongoDB, Cassandra, and Redis</p>

      <div className="benchmark-controls">
        <div className="buttons-group">
          <h3>Run Benchmarks</h3>
          <button
            onClick={() => runBenchmark('mongodb')}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Testing...' : 'Test MongoDB'}
          </button>
          <button
            onClick={() => runBenchmark('cassandra')}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Testing...' : 'Test Cassandra'}
          </button>
          <button
            onClick={() => runBenchmark('redis')}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Testing...' : 'Test Redis'}
          </button>
          <button
            onClick={runAllBenchmarks}
            disabled={loading}
            className="btn btn-success"
          >
            {loading ? 'Testing All...' : 'Run All Benchmarks'}
          </button>
        </div>

        {results && (
          <div className="metric-selector">
            <label>
              <input
                type="radio"
                value="avg_time"
                checked={selectedMetric === 'avg_time'}
                onChange={(e) => setSelectedMetric(e.target.value)}
              />
              Average Time (ms)
            </label>
            <label>
              <input
                type="radio"
                value="throughput"
                checked={selectedMetric === 'throughput'}
                onChange={(e) => setSelectedMetric(e.target.value)}
              />
              Throughput (ops/sec)
            </label>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading">Running benchmarks...</div>}

      {results && (
        <div className="results-container">
          <div className="results-summary">
            <h3>📊 Benchmark Summary</h3>
            {results.total_duration && <p>Duration: {results.total_duration.toFixed(2)} seconds</p>}
            <p>Timestamp: {new Date(results.timestamp).toLocaleString()}</p>
          </div>

          <div className="charts-grid">
            {chartData && (
              <div className="chart-card">
                <h3>Performance Comparison</h3>
                <div className="chart-wrapper">
                  <Bar
                    data={chartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: true,
                      plugins: {
                        legend: {
                          display: true,
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: selectedMetric === 'avg_time' 
                            ? 'Average Response Time (Lower is Better)' 
                            : 'Throughput (Higher is Better)',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                        },
                      },
                    }}
                  />
                </div>
              </div>
            )}

            {lineChartData && (
              <div className="chart-card">
                <h3>Response Time Trend</h3>
                <div className="chart-wrapper">
                  <Line
                    data={lineChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: true,
                      plugins: {
                        legend: {
                          display: true,
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: 'Response Time Across Multiple Calls',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          title: {
                            display: true,
                            text: 'Time (ms)',
                          },
                        },
                      },
                    }}
                  />
                </div>
              </div>
            )}
          </div>

          <div className="detailed-results">
            <h3>📈 Detailed Results</h3>
            <table className="results-table">
              <thead>
                <tr>
                  <th>Database</th>
                  <th>Avg Time (ms)</th>
                  <th>Min Time (ms)</th>
                  <th>Max Time (ms)</th>
                  <th>Throughput (ops/s)</th>
                  <th>Total Queries</th>
                </tr>
              </thead>
              <tbody>
                {results.benchmarks &&
                  Object.entries(results.benchmarks).map(([db, metrics]) => (
                    <tr key={db}>
                      <td className="db-name">{db}</td>
                      <td>{metrics.avg_time?.toFixed(2)}</td>
                      <td>{metrics.min_time?.toFixed(2)}</td>
                      <td>{metrics.max_time?.toFixed(2)}</td>
                      <td>{metrics.throughput?.toFixed(2)}</td>
                      <td>{metrics.total_queries}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {results.benchmarks && (
            <div className="winner-card">
              <h3>🏆 Performance Leader</h3>
              <p>
                Fastest Average Response Time:{' '}
                <strong>
                  {
                    Object.entries(results.benchmarks).sort(
                      ([, a], [, b]) => a.avg_time - b.avg_time
                    )[0][0]
                  }
                </strong>
              </p>
              <p>
                Highest Throughput:{' '}
                <strong>
                  {
                    Object.entries(results.benchmarks).sort(
                      ([, a], [, b]) => b.throughput - a.throughput
                    )[0][0]
                  }
                </strong>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Part5;
