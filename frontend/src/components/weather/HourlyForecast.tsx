import React from 'react';
import { HourlyForecast as HourlyType } from '../../types';
import { useWeather } from '../../contexts/WeatherContext';
import { getWeatherIcon } from './WeatherCard';
import { Umbrella, Wind } from 'lucide-react';

interface HourlyForecastProps {
  hourly: HourlyType[];
}

export const HourlyForecast: React.FC<HourlyForecastProps> = ({ hourly }) => {
  const { formatTemp, formatWind, formatHour, t } = useWeather();

  if (!hourly || hourly.length === 0) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
          {t('hourly_outlook_24h')}
        </h3>
        <span className="text-xs text-slate-400">{t('scroll_horizontally')}</span>
      </div>

      <div className="flex gap-2.5 overflow-x-auto pb-2 pt-1 scrollbar-thin">
        {hourly.map((item, idx) => (
          <div
            key={`${item.time}-${idx}`}
            className={`flex flex-col items-center justify-between min-w-[80px] p-2.5 rounded-lg border text-center flex-shrink-0 transition ${
              idx === 0
                ? 'bg-primary-50/50 dark:bg-primary-950/30 border-primary-200 dark:border-primary-800/80 shadow-xs'
                : 'bg-slate-50 dark:bg-slate-850 border-slate-100 dark:border-slate-800 hover:border-primary-400 dark:hover:border-primary-600'
            }`}
          >
            <span className={`text-xs font-semibold ${
              idx === 0
                ? 'text-primary-600 dark:text-primary-400 font-bold'
                : 'text-slate-600 dark:text-slate-300'
            }`}>
              {formatHour(item.time)}
            </span>

            <div className="my-2">
              {getWeatherIcon(item.condition_code, "w-6 h-6")}
            </div>

            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {formatTemp(item.temperature)}
            </span>

            {/* Rain Probability */}
            <div className="mt-1 flex items-center gap-0.5 text-[10px] text-blue-600 dark:text-blue-400 font-medium">
              <Umbrella className="w-2.5 h-2.5" />
              <span>{item.rain_probability}%</span>
            </div>

            {/* Wind */}
            <div className="mt-0.5 flex items-center gap-0.5 text-[9px] text-slate-400">
              <Wind className="w-2.5 h-2.5" />
              <span>{formatWind(item.wind_speed)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
