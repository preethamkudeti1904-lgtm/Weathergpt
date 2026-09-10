import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { WeatherProvider } from './contexts/WeatherContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Layout } from './components/layout/Layout';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { CurrentWeatherPage } from './pages/CurrentWeatherPage';
import { ForecastPage } from './pages/ForecastPage';
import { MapPage } from './pages/MapPage';
import { AlertsPage } from './pages/AlertsPage';
import { ChatPage } from './pages/ChatPage';
import { ClimatePage } from './pages/ClimatePage';
import { LocationsPage } from './pages/LocationsPage';
import { AdvisoryPage } from './pages/AdvisoryPage';
import { WindDirectionMapPage } from './pages/WindDirectionMapPage';
import { SettingsPage } from './pages/SettingsPage';

const AppContent: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>(() => {
    const path = window.location.pathname.replace('/', '').toLowerCase();
    if (path === 'wind-direction') return 'wind-direction';
    return localStorage.getItem('weathergpt_page') || 'dashboard';
  });

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
    localStorage.setItem('weathergpt_page', page);
    const newPath = page === 'dashboard' ? '/' : `/${page}`;
    if (window.location.pathname !== newPath) {
      window.history.pushState({}, '', newPath);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname.replace('/', '').toLowerCase();
      if (path === 'wind-direction') {
        setCurrentPage('wind-direction');
      } else if (path) {
        setCurrentPage(path);
      } else {
        setCurrentPage('dashboard');
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Standalone pages without dashboard sidebar
  if (currentPage === 'landing') {
    return <LandingPage onNavigate={handleNavigate} />;
  }

  if (currentPage === 'login') {
    return <LoginPage onNavigate={handleNavigate} />;
  }

  if (currentPage === 'register') {
    return <RegisterPage onNavigate={handleNavigate} />;
  }

  // Dashboard & Task-based pages wrapped in Layout
  return (
    <Layout currentPage={currentPage} onNavigate={handleNavigate}>
      {currentPage === 'dashboard' && <DashboardPage onNavigate={handleNavigate} />}
      {currentPage === 'current' && <CurrentWeatherPage />}
      {currentPage === 'forecast' && <ForecastPage />}
      {currentPage === 'map' && <MapPage />}
      {currentPage === 'alerts' && <AlertsPage />}
      {currentPage === 'chat' && <ChatPage />}
      {currentPage === 'climate' && <ClimatePage />}
      {currentPage === 'locations' && <LocationsPage />}
      {currentPage === 'advisory' && <AdvisoryPage />}
      {currentPage === 'wind-direction' && <WindDirectionMapPage />}
      {currentPage === 'settings' && <SettingsPage />}
    </Layout>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <WeatherProvider>
          <AppContent />
        </WeatherProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
