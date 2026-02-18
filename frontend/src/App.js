import React, { useState, useEffect } from 'react';
import './App.css';
import Part1 from './components/Part1';
import Part2 from './components/Part2';
import Part3 from './components/Part3';
import Part4 from './components/Part4';
import Part5 from './components/Part5';

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [darkMode, setDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode !== null ? JSON.parse(savedMode) : true;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  const tabs = [
    { label: 'Part 1: Statistics', component: <Part1 /> },
    { label: 'Part 2: Visualization', component: <Part2 /> },
    { label: 'Part 3: Regression', component: <Part3 /> },
    { label: 'Part 4: Classification', component: <Part4 /> },
    { label: 'Partie Annexe: Benchmark', component: <Part5 /> }
  ];

  return (
    <div className={`App ${darkMode ? 'dark-mode' : ''}`}>
      <header className="App-header">
        <div className="header-content">
          <h1>🐧 Penguins Analysis Platform</h1>
          <p>Multi-NoSQL Database Analysis & Classification</p>
        </div>
        <button 
          className="theme-toggle" 
          onClick={() => setDarkMode(!darkMode)}
          aria-label="Toggle dark mode"
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </header>

      <div className="tabs-container">
        <div className="tabs">
          {tabs.map((tab, index) => (
            <button
              key={index}
              className={`tab-button ${activeTab === index ? 'active' : ''}`}
              onClick={() => setActiveTab(index)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="content-container">
        {tabs[activeTab].component}
      </div>

      <footer className="App-footer">
        <p>Penguins Analysis Platform v1.0 | MongoDB | Cassandra | Redis</p>
      </footer>
    </div>
  );
}

export default App;
