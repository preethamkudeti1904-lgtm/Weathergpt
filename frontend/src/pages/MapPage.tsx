import React from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { WeatherMap } from '../components/map/WeatherMap';

export const MapPage: React.FC = () => {
  const { location, t } = useWeather();

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">
          {t('weatherMap')}
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          {t('satellite_imagery')} ({location})
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 p-2 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <WeatherMap />
      </div>
    </div>
  );
};
