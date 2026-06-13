import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import MainPage from './pages/MainPage';
import CertifyPage from './pages/CertifyPage';
import ScanningPage from './pages/ScanningPage';
import ResultPage from './pages/ResultPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AutomationPage from './pages/AutomationPage';
import NotificationPage from './pages/NotificationPage';
import AccountPage from './pages/AccountPage';

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/certify" element={<CertifyPage />} />
        <Route path="/scanning/:taskId" element={<ScanningPage />} />
        <Route path="/result/:taskId" element={<ResultPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/automation" element={<AutomationPage />} />
        <Route path="/notifications" element={<NotificationPage />} />
        <Route path="/account" element={<AccountPage />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
