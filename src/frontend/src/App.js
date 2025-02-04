import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import BostonPage from './pages/BostonPage';
import SFPage from './pages/SFPage';
import './styles/CommentVisualizer.css';
import './styles/darkTheme.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/boston" element={<BostonPage />} />
          <Route path="/sf" element={<SFPage />} />
          <Route path="/" element={<BostonPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
