import React from 'react';
import { CurrentWeather } from '../../types';
import { useWeather } from '../../contexts/WeatherContext';
import {
  Sun,
  Cloud,
  CloudRain,
  CloudLightning,
  CloudFog,
  Wind,
  Droplets,
  Compass,
  Gauge,
  Eye,
  Umbrella,
  Sunrise,
  Sunset,
  RefreshCw
} from 'lucide-react';

interface WeatherCardProps {
  weather: CurrentWeather;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const getWeatherIcon = (code: number, className = "w-8 h-8") => {
  if (code === 0) return <Sun className={`${className} text-amber-500`} />;
  if (code <= 3) return <Cloud className={`${className} text-slate-400 dark:text-slate-300`} />;
  if (code === 45 || code === 48) return <CloudFog className={`${className} text-slate-400`} />;
  if (code >= 51 && code <= 67) return <CloudRain className={`${className} text-blue-500`} />;
  if (code >= 80 && code <= 82) return <CloudRain className={`${className} text-blue-600`} />;
  if (code >= 95) return <CloudLightning className={`${className} text-purple-500`} />;
  return <Cloud className={`${className} text-slate-400`} />;
};

export const WeatherCard: React.FC<WeatherCardProps> = ({ weather, onRefresh, isRefreshing }) => {
  const { formatTemp, formatWind, formatUpdated, translateCondition, t } = useWeather();

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
      {/* Top Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-primary-600 dark:text-primary-400 uppercase tracking-wider">
            {t('live_meteorology')}
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-0.5">
            {weather.location_name}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Lat: {weather.latitude.toFixed(2)}°, Lon: {weather.longitude.toFixed(2)}°
          </p>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title={t('refresh_weather')}
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
        )}
      </div>

      {/* Main Temperature & Condition Display */}
      <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-3 border-y border-slate-100 dark:border-slate-800/80">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
            {getWeatherIcon(weather.condition_code, "w-12 h-12")}
          </div>
          <div>
            <div className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              {formatTemp(weather.temperature)}
            </div>
            <div className="text-sm font-medium text-slate-600 dark:text-slate-300 mt-0.5">
              {translateCondition(weather.condition)}
            </div>
          </div>
        </div>

        <div className="text-left sm:text-right">
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {t('temp_feels_like')} <span className="font-semibold text-slate-700 dark:text-slate-200">{formatTemp(weather.feels_like)}</span>
          </div>
          {weather.uv_index !== undefined && weather.uv_index !== null && (
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {t('uv_index')}: <span className="font-semibold text-amber-600 dark:text-amber-400">{weather.uv_index}</span>
            </div>
          )}
          <div className="flex items-center sm:justify-end gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
            {weather.sunrise && (
              <span className="flex items-center gap-1">
                <Sunrise className="w-3.5 h-3.5 text-amber-500" /> {weather.sunrise}
              </span>
            )}
            {weather.sunset && (
              <span className="flex items-center gap-1">
                <Sunset className="w-3.5 h-3.5 text-orange-500" /> {weather.sunset}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Grid of Meteorological Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 mt-4">
        {/* Humidity */}
        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Droplets className="w-3.5 h-3.5 text-blue-500" />
            <span>{t('humidity')}</span>
          </div>
          <div className="text-base font-bold text-slate-800 dark:text-slate-100 mt-1">
            {weather.humidity}%
          </div>
        </div>

        {/* Wind */}
        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Wind className="w-3.5 h-3.5 text-teal-500" />
            <span>{t('wind')}</span>
          </div>
          <div className="text-base font-bold text-slate-800 dark:text-slate-100 mt-1 truncate">
            {formatWind(weather.wind_speed)}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">
            {weather.wind_direction_cardinal} ({weather.wind_direction}°)
          </div>
        </div>

        {/* Pressure */}
        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Gauge className="w-3.5 h-3.5 text-indigo-500" />
            <span>{t('pressure')}</span>
          </div>
          <div className="text-base font-bold text-slate-800 dark:text-slate-100 mt-1">
            {weather.pressure} hPa
          </div>
        </div>

        {/* Visibility */}
        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Eye className="w-3.5 h-3.5 text-emerald-500" />
            <span>{t('visibility')}</span>
          </div>
          <div className="text-base font-bold text-slate-800 dark:text-slate-100 mt-1">
            {weather.visibility} km
          </div>
        </div>

        {/* Precipitation */}
        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Umbrella className="w-3.5 h-3.5 text-cyan-500" />
            <span>{t('precipitation')}</span>
          </div>
          <div className="text-base font-bold text-slate-800 dark:text-slate-100 mt-1">
            {(() => {
              const precip = weather.current?.precipitation !== undefined ? weather.current.precipitation : weather.precipitation;
              if (precip !== null && precip !== undefined && !Number.isNaN(precip)) {
                return `${precip} mm`;
              }
              return 'Unavailable';
            })()}
          </div>
        </div>

        {/* Wind Direction */}
        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Compass className="w-3.5 h-3.5 text-rose-500" />
            <span>{t('bearing')}</span>
          </div>
          <div className="text-base font-bold text-slate-800 dark:text-slate-100 mt-1">
            {weather.wind_direction_cardinal}
          </div>
        </div>
      </div>

      {/* Source and Updated Attribution Bar (Mandatory Requirement) */}
      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 gap-1">
        <div>
          <span className="font-semibold">{t('source_label')}:</span> {weather.source}
        </div>
        <div>
          <span className="font-semibold">{t('updated_label')}:</span> {formatUpdated(weather.updated_at)}
        </div>
      </div>
    </div>
  );
};
