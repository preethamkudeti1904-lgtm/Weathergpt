import React, { useState } from 'react';
import { DailyForecast as DailyType } from '../../types';
import { useWeather } from '../../contexts/WeatherContext';
import { getWeatherIcon } from './WeatherCard';
import { Umbrella, Wind, Sunrise, Sunset } from 'lucide-react';

interface DailyForecastProps {
  daily: DailyType[];
}

export const DailyForecast: React.FC<DailyForecastProps> = ({ daily }) => {
  const { formatTemp, formatWind, formatDate, translateCondition, t } = useWeather();
  const [selectedDay, setSelectedDay] = useState<number>(0);

  if (!daily || daily.length === 0) return null;

  const active = daily[selectedDay] || daily[0];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
          {t('seven_day_outlook')}
        </h3>
        <span className="text-xs text-slate-400">{t('click_day_details')}</span>
      </div>

      <div className="space-y-2">
        {daily.map((item, idx) => {
          const isSelected = selectedDay === idx;
          return (
            <div
              key={`${item.date}-${idx}`}
              onClick={() => setSelectedDay(idx)}
              className={`p-3 rounded-lg border cursor-pointer transition flex items-center justify-between gap-3 ${
                isSelected
                  ? 'border-primary-500 bg-primary-50/40 dark:bg-primary-950/30'
                  : 'border-slate-100 dark:border-slate-800/80 hover:bg-slate-50 dark:hover:bg-slate-850'
              }`}
            >
              {/* Day & Date */}
              <div className="w-24 sm:w-28 flex-shrink-0">
                <div className="font-semibold text-xs text-slate-900 dark:text-white">
                  {idx === 0 ? t('today') : idx === 1 ? t('tomorrow') : item.day_name}
                </div>
                <div className="text-[11px] text-slate-400">{formatDate(item.date)}</div>
              </div>

              {/* Weather Icon & Condition */}
              <div className="flex items-center gap-2 flex-1 min-w-0">
                {getWeatherIcon(item.condition_code, "w-6 h-6 flex-shrink-0")}
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300 truncate hidden sm:inline">
                  {translateCondition(item.condition)}
                </span>
              </div>

              {/* Rain probability */}
              <div className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 w-14 flex-shrink-0">
                <Umbrella className="w-3.5 h-3.5" />
                <span>{item.rain_probability}%</span>
              </div>

              {/* Wind */}
              <div className="hidden md:flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400 w-20 flex-shrink-0">
                <Wind className="w-3.5 h-3.5 text-teal-500" />
                <span className="truncate">{formatWind(item.wind_speed_max)}</span>
              </div>

              {/* Temp Min - Max Bar */}
              <div className="flex items-center gap-2 w-28 sm:w-32 justify-end flex-shrink-0 text-xs">
                <span className="font-medium text-slate-400">
                  {formatTemp(item.temp_min)}
                </span>
                <div className="w-12 sm:w-16 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden flex">
                  <div
                    className="bg-primary-500 rounded-full h-full"
                    style={{ width: `${Math.min(100, Math.max(20, (item.temp_max / 45) * 100))}%` }}
                  />
                </div>
                <span className="font-bold text-slate-900 dark:text-white">
                  {formatTemp(item.temp_max)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Day Detail Drawer */}
      {active && (
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs flex flex-wrap items-center justify-between gap-4 text-slate-600 dark:text-slate-300">
          <div>
            <span className="font-semibold text-slate-900 dark:text-white">{active.day_name} ({formatDate(active.date)}):</span>{' '}
            {translateCondition(active.condition)} ({t('rain_chance')}: {active.rain_probability}%, {t('expected_precip')}: {active.precipitation} mm).
          </div>
          <div className="flex items-center gap-4 text-slate-500 dark:text-slate-400">
            {active.sunrise && (
              <span className="flex items-center gap-1">
                <Sunrise className="w-3.5 h-3.5 text-amber-500" /> {t('sunrise')}: {active.sunrise}
              </span>
            )}
            {active.sunset && (
              <span className="flex items-center gap-1">
                <Sunset className="w-3.5 h-3.5 text-orange-500" /> {t('sunset')}: {active.sunset}
              </span>
            )}
            {active.uv_index_max && (
              <span>{t('max_uv')}: <strong className="text-slate-800 dark:text-slate-200">{active.uv_index_max}</strong></span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
