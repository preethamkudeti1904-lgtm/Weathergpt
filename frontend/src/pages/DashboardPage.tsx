import React from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { useAuth } from '../contexts/AuthContext';
import { canAccessAdvisory } from '../utils/permissions';
import { WeatherCard } from '../components/weather/WeatherCard';
import { HourlyForecast } from '../components/weather/HourlyForecast';
import { DailyForecast } from '../components/weather/DailyForecast';
import { AlertBanner } from '../components/weather/AlertBanner';
import { WeatherMap } from '../components/map/WeatherMap';
import {
  Bot,
  CalendarDays,
  Map as MapIcon,
  AlertTriangle,
  ArrowRight,
  Sprout,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  MapPin
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (page: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const {
    currentLocation,
    location,
    latitude,
    longitude,
    accuracy,
    locationSource,
    gpsStatus,
    gpsError,
    useMyLocation,
    timezone,
    timezoneAbbreviation,
    weather,
    forecast,
    alerts,
    isLoading,
    refreshWeather,
    formatUpdated,
    t
  } = useWeather();
  const { user } = useAuth();

  const userType = user?.user_type || 'General User';

  return (
    <div className="space-y-6">
      {/* Quick Action Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white dark:bg-slate-900 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">{t('quick_actions') || 'Quick Actions:'}</span>
          <button
            onClick={() => onNavigate('chat')}
            className="px-3 py-1.5 rounded-lg bg-primary-50 dark:bg-primary-950/60 text-primary-700 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-primary-900/60 text-xs font-semibold flex items-center gap-1.5 transition border border-primary-200/60 dark:border-primary-800/60"
          >
            <Bot className="w-3.5 h-3.5 text-primary-600" />
            <span>{t('ask_weathergpt') || 'Ask WeatherGPT'}</span>
          </button>
          <button
            onClick={() => onNavigate('forecast')}
            className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-750 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <CalendarDays className="w-3.5 h-3.5 text-slate-500" />
            <span>{t('forecast')}</span>
          </button>
          <button
            onClick={() => onNavigate('map')}
            className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-750 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <MapIcon className="w-3.5 h-3.5 text-slate-500" />
            <span>{t('weatherMap')}</span>
          </button>
          <button
            onClick={() => onNavigate('alerts')}
            className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-750 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            <span>{t('alerts')}</span>
          </button>
        </div>

        {/* Role Shortcut (Farmer Only) */}
        {canAccessAdvisory(user) && (
          <button
            onClick={() => onNavigate('advisory')}
            className="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1"
          >
            <span>{t('advisory')}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Dedicated Central Location & Live GPS Card */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 sm:p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`p-2.5 rounded-xl flex items-center justify-center flex-shrink-0 ${
              locationSource === 'gps'
                ? 'bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400'
                : locationSource === 'default'
                ? 'bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400'
                : 'bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400'
            }`}>
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  {locationSource === 'default'
                    ? 'DEFAULT LOCATION'
                    : locationSource === 'gps'
                    ? 'GPS LOCATION'
                    : locationSource === 'ip_approximate'
                    ? 'APPROXIMATE LOCATION'
                    : t('current_location')}
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  locationSource === 'gps'
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                    : locationSource === 'default'
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800'
                    : locationSource === 'ip_approximate'
                    ? 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                    : 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
                }`}>
                  {locationSource === 'gps'
                    ? t('gps_active')
                    : locationSource === 'default'
                    ? 'DEFAULT'
                    : locationSource === 'ip_approximate'
                    ? 'APPROXIMATE'
                    : locationSource === 'map_click'
                    ? t('map_pinpoint')
                    : t('station_search')}
                </span>
              </div>

              {/* Exact Locality Name as Primary */}
              <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mt-0.5">
                {currentLocation.name || location.split(',')[0]}
              </h2>

              {/* District, State, Country Hierarchy */}
              {(currentLocation.district || currentLocation.state || currentLocation.country) && (
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                  {[
                    currentLocation.district && (currentLocation.district !== currentLocation.name ? `${currentLocation.district}` : null),
                    currentLocation.state,
                    currentLocation.country
                  ].filter(Boolean).join(', ')}
                </div>
              )}

              <div className="flex flex-wrap items-center gap-2.5 text-xs text-slate-500 dark:text-slate-400 mt-1.5 font-mono">
                <span>{latitude >= 0 ? `${latitude.toFixed(4)}° N` : `${Math.abs(latitude).toFixed(4)}° S`}</span>
                <span>•</span>
                <span>{longitude >= 0 ? `${longitude.toFixed(4)}° E` : `${Math.abs(longitude).toFixed(4)}° W`}</span>
                <span>•</span>
                <span className="font-sans font-medium text-slate-600 dark:text-slate-300">
                  {timezone} ({timezoneAbbreviation})
                </span>
                {accuracy !== null && (
                  <>
                    <span>•</span>
                    <span className="font-sans font-semibold text-emerald-600 dark:text-emerald-400">
                      {t('gps_accuracy')}: ±{Math.round(accuracy)} m
                    </span>
                  </>
                )}
                {weather?.updated_at && (
                  <>
                    <span>•</span>
                    <span className="font-sans text-slate-400">
                      {formatUpdated(weather.updated_at)}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-center">
            <button
              onClick={useMyLocation}
              disabled={gpsStatus === 'loading'}
              className="px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-2 transition shadow-sm"
              title={t('use_my_location')}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${gpsStatus === 'loading' ? 'animate-spin' : ''}`} />
              <span>{gpsStatus === 'loading' ? t('getting_location') : t('use_my_location')}</span>
            </button>
          </div>
        </div>

        {/* Low Accuracy Warning (Section 8: accuracy > 1000m) */}
        {accuracy !== null && accuracy > 1000 && (
          <div className="mt-3 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 flex items-center justify-between text-xs text-amber-800 dark:text-amber-200">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>Location accuracy is low (±{Math.round(accuracy)}m). GPS signal may be coarse or obstructed.</span>
            </div>
            <button
              onClick={useMyLocation}
              className="ml-3 px-2.5 py-1 rounded bg-amber-600 text-white text-[11px] font-semibold hover:bg-amber-700 transition flex-shrink-0"
            >
              Retry GPS
            </button>
          </div>
        )}

        {/* Honest GPS Permission Denial / Error Warning (Section 20) */}
        {gpsError && (
          <div className="mt-3 p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-xs text-red-700 dark:text-red-300">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="font-semibold">GPS permission is unavailable.</span>
                <span className="ml-1 text-red-600 dark:text-red-400">({gpsError})</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onNavigate('locations')}
                  className="px-2.5 py-1 rounded bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 text-slate-800 dark:text-slate-200 text-[11px] font-medium transition"
                >
                  Search Location
                </button>
                <button
                  onClick={useMyLocation}
                  className="px-2.5 py-1 rounded bg-red-600 hover:bg-red-700 text-white text-[11px] font-semibold transition"
                >
                  Retry GPS
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Top: Current Weather Card */}
      {weather ? (
        <WeatherCard weather={weather} onRefresh={refreshWeather} isRefreshing={isLoading} />
      ) : (
        <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <RefreshCw className="w-6 h-6 animate-spin text-primary-500 mx-auto mb-2" />
          <p className="text-xs text-slate-500">{t('searching_real_locations')} {location}...</p>
        </div>
      )}

      {/* Middle Grid: Forecast & Alerts Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Hourly & 7-Day Forecast */}
        <div className="lg:col-span-2 space-y-6">
          {forecast?.hourly && <HourlyForecast hourly={forecast.hourly} />}
          {forecast?.daily && <DailyForecast daily={forecast.daily} />}
        </div>

        {/* Right 1 Col: Alerts & AI Prompt Suggestion */}
        <div className="space-y-6">
          {/* Active Alerts Preview */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                {t('threat_surveillance')} (NDMA / SACHET)
              </h3>
              <button
                onClick={() => onNavigate('alerts')}
                className="text-[11px] text-primary-600 dark:text-primary-400 font-semibold hover:underline"
              >
                {t('all_alerts')} →
              </button>
            </div>
            <AlertBanner alertsData={alerts} />

          </div>

          {/* Quick AI Conversational Prompt Box */}
          <div className="bg-gradient-to-br from-primary-900 to-slate-900 text-white rounded-xl p-5 shadow-sm border border-primary-800">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-primary-400" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-primary-300">
                {t('weatherGPT')}
              </h4>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {t('ask_natural_questions')}
            </p>
            <div className="mt-3 space-y-1.5">
              <button
                onClick={() => onNavigate('chat')}
                className="w-full text-left p-2 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-slate-200 transition"
              >
                "Will it rain tomorrow in {location.split(',')[0]}?"
              </button>
              <button
                onClick={() => onNavigate('chat')}
                className="w-full text-left p-2 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-slate-200 transition"
              >
                "Is it safe to travel today?"
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Weather Map Preview */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              {t('satellite_imagery')}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {t('interactive_radar_desc')}
            </p>
          </div>
          <button
            onClick={() => onNavigate('map')}
            className="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1"
          >
            <span>{t('full_map_view')}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <WeatherMap />
      </div>
    </div>
  );
};
