import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { windService, NormalizedWindData, WindPoint, degreesToCardinal } from '../services/windService';
import { api } from '../services/api';
import { LocationItem } from '../types';
import { WindCompass } from '../components/wind/WindCompass';
import { WindLegend } from '../components/wind/WindLegend';
import { WindTimeSlider } from '../components/wind/WindTimeSlider';
import { WindMapCanvas } from '../components/wind/WindMapCanvas';
import {
  Wind,
  Compass,
  Navigation,
  MapPin,
  Search,
  Crosshair,
  RotateCw,
  Clock,
  AlertCircle,
  Gauge,
  Sparkles,
  Loader2,
  Calendar
} from 'lucide-react';
import { formatLocalTime, getTimezoneAbbreviation } from '../services/timezoneService';

export const WindDirectionMapPage: React.FC = () => {
  const {
    currentLocation,
    latitude,
    longitude,
    location,
    timezone,
    useMyLocation,
    setCoordinates,
    gpsStatus,
    gpsError,
    refreshWeather,
    t
  } = useWeather();

  const [windData, setWindData] = useState<NormalizedWindData | null>(null);
  const [selectedHourIndex, setSelectedHourIndex] = useState<number>(-1); // -1 = Live, 0..23 = Hourly
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<LocationItem[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState<boolean>(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Fetch wind data whenever central location changes
  const loadWindData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await windService.getWindData(latitude, longitude, currentLocation.name, timezone);
      setWindData(data);
      setSelectedHourIndex(-1); // Reset to live on location change
    } catch (err) {
      console.error('[WindMap] Error loading wind data:', err);
      setError(t('unable_retrieve_wind') || 'Unable to retrieve current wind data.');
    } finally {
      setIsLoading(false);
    }
  }, [latitude, longitude, currentLocation.name, timezone, t]);

  useEffect(() => {
    loadWindData();
  }, [loadWindData]);

  // Handle Location Search
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await api.searchLocations(searchQuery);
        setSearchResults(results);
      } catch (err) {
        console.error('[WindMap] Search error:', err);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside to close search dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowSearchDropdown(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const handleSelectSearchItem = (item: LocationItem) => {
    setShowSearchDropdown(false);
    setSearchQuery('');
    setCoordinates(item.latitude, item.longitude, 'search', item.name);
  };

  const handleUseMyLocation = async () => {
    try {
      await useMyLocation();
    } catch (err) {
      console.error('[WindMap] GPS error:', err);
    }
  };

  const handleRefresh = async () => {
    windService.invalidateCache(latitude, longitude);
    await refreshWeather();
    await loadWindData();
  };

  // Determine active wind vector (Live vs Scrubber hour)
  const activeWindPoint: WindPoint | null = windData
    ? selectedHourIndex === -1
      ? windData.current
      : windData.hourly[selectedHourIndex] || windData.current
    : null;

  const tzAbbr = getTimezoneAbbreviation(windData?.timezone || timezone);

  const localUpdatedDisplay = windData
    ? formatLocalTime(windData.updatedAt, windData.timezone, false, 'en') + ` ${tzAbbr}`
    : '--';

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Title & Subtitle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
              <Wind className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                {t('wind_map_title')}
              </h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                {t('wind_map_subtitle')}
              </p>
            </div>
          </div>
        </div>

        {/* Global Action Bar: Search, GPS, Refresh */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Geocoded Location Search */}
          <div ref={searchRef} className="relative flex-1 sm:w-64">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setShowSearchDropdown(true);
                }}
                onFocus={() => setShowSearchDropdown(true)}
                placeholder={t('search_placeholder')}
                className="w-full pl-9 pr-8 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm"
              />
              {isSearching && (
                <Loader2 className="w-3.5 h-3.5 text-slate-400 animate-spin absolute right-3 top-1/2 -translate-y-1/2" />
              )}
            </div>

            {/* Search Dropdown */}
            {showSearchDropdown && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 max-h-60 overflow-y-auto">
                {searchResults.map((item) => (
                  <button
                    key={`${item.latitude}-${item.longitude}-${item.name}`}
                    onClick={() => handleSelectSearchItem(item)}
                    className="w-full text-left px-3.5 py-2.5 text-xs hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 last:border-0"
                  >
                    <MapPin className="w-3.5 h-3.5 text-sky-500 flex-shrink-0" />
                    <div>
                      <div className="font-semibold text-slate-800 dark:text-slate-100">
                        {item.name}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {item.state ? `${item.state}, ` : ''}{item.country || 'Global'} &bull; {item.latitude.toFixed(3)}°, {item.longitude.toFixed(3)}°
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Use My Location GPS */}
          <button
            onClick={handleUseMyLocation}
            disabled={gpsStatus === 'loading'}
            title="Use My Location GPS"
            className="px-3.5 py-2 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-sm transition disabled:opacity-50"
          >
            {gpsStatus === 'loading' ? (
              <Loader2 className="w-3.5 h-3.5 text-sky-500 animate-spin" />
            ) : (
              <Crosshair className="w-3.5 h-3.5 text-sky-500" />
            )}
            <span className="hidden sm:inline">{t('use_my_location')}</span>
          </button>

          {/* Refresh Live Data */}
          <button
            onClick={handleRefresh}
            title="Refresh Real-time Wind"
            className="p-2 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm transition"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* GPS Error Alert */}
      {gpsError && (
        <div className="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-xs text-amber-800 dark:text-amber-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{gpsError}</span>
        </div>
      )}

      {/* Active Location Info Strip */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-sky-600 dark:text-sky-400 flex-shrink-0" />
          <div>
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
              {currentLocation.name}
            </span>
            <span className="text-[11px] text-slate-400 ml-2">
              ({latitude.toFixed(4)}°N, {longitude.toFixed(4)}°E) &bull; {tzAbbr}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            <span>Updated: {localUpdatedDisplay}</span>
          </div>
          <span className="hidden md:inline px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-mono">
            {windData?.source || 'Open-Meteo'}
          </span>
        </div>
      </div>

      {/* Main Grid: Left Panels (Cards + Compass + Legend) & Right Panel (Interactive Leaflet Map) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Current Wind Information Card + Compass + Legend (5 cols) */}
        <div className="lg:col-span-5 space-y-6 order-2 lg:order-1">
          {/* Section 5: Current Wind Information Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-400 border border-sky-100 dark:border-sky-900/40">
                  <Gauge className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                    {t('current_wind')}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {selectedHourIndex === -1 ? 'Real-time Surface Wind' : `Forecast Hour (+${selectedHourIndex + 1}h)`}
                  </p>
                </div>
              </div>

              {activeWindPoint && (
                <span
                  className="px-2.5 py-1 text-xs font-semibold rounded-lg text-white shadow-sm"
                  style={{ backgroundColor: activeWindPoint.beaufortScale.color }}
                >
                  {t(activeWindPoint.beaufortScale.labelKey)}
                </span>
              )}
            </div>

            {/* Metrics Display Grid */}
            {isLoading ? (
              <div className="py-8 flex flex-col items-center justify-center gap-2 text-slate-400 text-xs">
                <Loader2 className="w-6 h-6 animate-spin text-sky-500" />
                <span>Loading meteorological wind vectors...</span>
              </div>
            ) : error ? (
              <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 rounded-xl text-xs text-red-600 dark:text-red-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            ) : activeWindPoint ? (
              <div className="grid grid-cols-2 gap-3">
                {/* Wind Direction Cardinal */}
                <div className="bg-slate-50 dark:bg-slate-850/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <div className="text-xs text-slate-400 dark:text-slate-500 font-medium">
                    {t('wind_direction')}
                  </div>
                  <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                    {activeWindPoint.windDirectionCardinal || degreesToCardinal(activeWindPoint.windDirection)}
                  </div>
                  <div className="text-xs text-sky-600 dark:text-sky-400 font-mono mt-0.5">
                    {activeWindPoint.windDirection !== null ? `${activeWindPoint.windDirection}°` : t('wind_data_unavailable')}
                  </div>
                </div>

                {/* Wind Speed */}
                <div className="bg-slate-50 dark:bg-slate-850/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <div className="text-xs text-slate-400 dark:text-slate-500 font-medium">
                    {t('wind_speed')}
                  </div>
                  <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                    {activeWindPoint.windSpeed !== null ? `${activeWindPoint.windSpeed}` : '--'}{' '}
                    <span className="text-xs font-normal text-slate-400">km/h</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    {activeWindPoint.windSpeed !== null ? `${(activeWindPoint.windSpeed / 3.6).toFixed(1)} m/s` : '--'}
                  </div>
                </div>

                {/* Wind Gust */}
                <div className="bg-slate-50 dark:bg-slate-850/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <div className="text-xs text-slate-400 dark:text-slate-500 font-medium">
                    {t('wind_gusts')}
                  </div>
                  <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                    {activeWindPoint.windGust !== null ? `${activeWindPoint.windGust}` : '--'}{' '}
                    <span className="text-xs font-normal text-slate-400">km/h</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    Peak Gust Speed
                  </div>
                </div>

                {/* Selected Location */}
                <div className="bg-slate-50 dark:bg-slate-850/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800">
                  <div className="text-xs text-slate-400 dark:text-slate-500 font-medium truncate">
                    {t('selected_location')}
                  </div>
                  <div className="text-sm font-bold text-slate-900 dark:text-white mt-1 truncate" title={currentLocation.name}>
                    {currentLocation.city || currentLocation.name.split(',')[0]}
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    {tzAbbr}
                  </div>
                </div>
              </div>
            ) : null}

            {/* Met Description & Source Citation */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
              <span>{windData?.source || 'Open-Meteo Surface Analysis'}</span>
              <span>Local: {localUpdatedDisplay}</span>
            </div>
          </div>

          {/* Section 6: Dynamic Wind Compass */}
          <WindCompass
            degrees={activeWindPoint?.windDirection ?? null}
            speed={activeWindPoint?.windSpeed ?? null}
            cardinal={activeWindPoint?.windDirectionCardinal}
            t={t}
          />

          {/* Section 7: WMO Beaufort Wind Speed Legend */}
          <WindLegend currentSpeed={activeWindPoint?.windSpeed} t={t} />
        </div>

        {/* Right Side: Large Interactive Leaflet Wind Map (7 cols) */}
        <div className="lg:col-span-7 space-y-6 order-1 lg:order-2">
          {activeWindPoint ? (
            <WindMapCanvas
              latitude={latitude}
              longitude={longitude}
              locationName={currentLocation.name}
              activeWindPoint={activeWindPoint}
              onUseLocation={(lat, lon, name) => {
                setCoordinates(lat, lon, 'map_click', name);
              }}
              t={t}
            />
          ) : (
            <div className="w-full h-[520px] rounded-2xl border border-slate-200 dark:border-slate-800 flex items-center justify-center bg-slate-100 dark:bg-slate-900 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-sky-500" />
            </div>
          )}

          {/* Section 8 & 9: 24-Hour Forecast Time Slider & Hourly Strip */}
          {windData && (
            <WindTimeSlider
              hourlyPoints={windData.hourly}
              currentPoint={windData.current}
              selectedIndex={selectedHourIndex}
              onSelectIndex={setSelectedHourIndex}
              timezone={windData.timezone}
              t={t}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default WindDirectionMapPage;
