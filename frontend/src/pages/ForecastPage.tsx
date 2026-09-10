import React from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { HourlyForecast } from '../components/weather/HourlyForecast';
import { DailyForecast } from '../components/weather/DailyForecast';

export const ForecastPage: React.FC = () => {
  const { forecast, location, t } = useWeather();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">
          {t('forecast')}
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          {t('seven_day_forecast')} ({location})
        </p>
      </div>

      {forecast?.hourly && <HourlyForecast hourly={forecast.hourly} />}
      {forecast?.daily && <DailyForecast daily={forecast.daily} />}
    </div>
  );
};
