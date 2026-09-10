import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useWeather } from '../contexts/WeatherContext';
import { FarmerAdvisory } from '../components/roles/FarmerAdvisory';
import { DisasterDashboard } from '../components/roles/DisasterDashboard';
import { AviationWeather } from '../components/roles/AviationWeather';
import { MarineWeather } from '../components/roles/MarineWeather';
import { ResearcherAnalytics } from '../components/roles/ResearcherAnalytics';
import { Sprout, ShieldAlert, Plane, Waves, BarChart3 } from 'lucide-react';

export const AdvisoryPage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useWeather();
  const userType = user?.user_type || 'General User';

  const [activeTab, setActiveTab] = useState<string>(() => {
    if (userType === 'Farmer') return 'farmer';
    if (userType === 'Disaster Management') return 'disaster';
    if (userType === 'Aviation') return 'aviation';
    if (userType === 'Marine') return 'marine';
    if (userType === 'Researcher') return 'researcher';
    return 'farmer';
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">
            {t('advisory')}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            {t('user_mode_label')}: {t('preferences_units')}
          </p>
        </div>

        {/* Sector Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-x-auto text-xs">
          <button
            onClick={() => setActiveTab('farmer')}
            className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'farmer'
                ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Sprout className="w-3.5 h-3.5" />
            <span>{t('role_farmer')}</span>
          </button>

          <button
            onClick={() => setActiveTab('disaster')}
            className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'disaster'
                ? 'bg-white dark:bg-slate-900 text-red-600 dark:text-red-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{t('role_disaster')}</span>
          </button>

          <button
            onClick={() => setActiveTab('aviation')}
            className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'aviation'
                ? 'bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Plane className="w-3.5 h-3.5" />
            <span>{t('role_aviation')}</span>
          </button>

          <button
            onClick={() => setActiveTab('marine')}
            className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'marine'
                ? 'bg-white dark:bg-slate-900 text-cyan-600 dark:text-cyan-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Waves className="w-3.5 h-3.5" />
            <span>{t('role_marine')}</span>
          </button>

          <button
            onClick={() => setActiveTab('researcher')}
            className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
              activeTab === 'researcher'
                ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>{t('role_researcher')}</span>
          </button>
        </div>
      </div>

      {activeTab === 'farmer' && <FarmerAdvisory />}
      {activeTab === 'disaster' && <DisasterDashboard />}
      {activeTab === 'aviation' && <AviationWeather />}
      {activeTab === 'marine' && <MarineWeather />}
      {activeTab === 'researcher' && <ResearcherAnalytics />}
    </div>
  );
};
