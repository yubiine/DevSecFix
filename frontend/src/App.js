import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import MainPage from './pages/MainPage';
import CertifyPage from './pages/CertifyPage';
import ScanningPage from './pages/ScanningPage';
import ResultPage from './pages/ResultPage';

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/certify" element={<CertifyPage />} />
        <Route path="/scanning/:taskId" element={<ScanningPage />} />
        <Route path="/result/:taskId" element={<ResultPage />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
