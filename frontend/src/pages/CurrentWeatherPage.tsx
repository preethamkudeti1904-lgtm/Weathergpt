import React from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { WeatherCard } from '../components/weather/WeatherCard';
import { RefreshCw, AlertCircle } from 'lucide-react';

export const CurrentWeatherPage: React.FC = () => {
  const { weather, location, isLoading, error, refreshWeather, t } = useWeather();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">
          {t('currentWeather')}
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          {t('verified_met_observations')}
        </p>
      </div>

      {error ? (
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 text-xs text-amber-800 dark:text-amber-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{t('weather_unavailable')}</span>
          </div>
          <button
            onClick={refreshWeather}
            className="px-3 py-1 rounded bg-amber-200 dark:bg-amber-900 text-amber-900 dark:text-amber-100 font-semibold"
          >
            {t('retry')}
          </button>
        </div>
      ) : weather ? (
        <WeatherCard weather={weather} onRefresh={refreshWeather} isRefreshing={isLoading} />
      ) : (
        <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <RefreshCw className="w-6 h-6 animate-spin text-primary-500 mx-auto mb-2" />
          <p className="text-xs text-slate-500">{t('searching_real_locations')} {location}...</p>
        </div>
      )}
    </div>
  );
};
