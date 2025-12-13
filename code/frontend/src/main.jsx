import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './styles/globals.css';
import './styles/remaike-ui.css';
// remAIke full template CSS removed to avoid global conflicts; using scoped remaike-ui.css instead.

/**
 * remAIke.TV - RetroTV Manager
 *
 * Entry point for the React application.
 * Mounts the App component with global styles.
 */
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
