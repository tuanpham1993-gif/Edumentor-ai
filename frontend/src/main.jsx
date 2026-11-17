import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import { initTheme } from './utils/theme.js';
import './styles/index.css'; // CSS dùng chung (global) — xem src/styles/
import '@xyflow/react/dist/style.css';
initTheme();

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
