import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { CurrentWeather, ForecastData, AlertsData, CentralLocation } from '../types';
import { api } from '../services/api';
import { locationService, GpsStatus } from '../services/locationService';
import { LanguageCode, translations, translateCondition } from '../i18n/translations';
import {
  formatLocalTimeWithAbbr,
  getTimezoneAbbreviation,
  formatLocalHour as tzFormatHour,
  formatLocalDate as tzFormatDate,
  formatUpdatedTime as tzFormatUpdated
} from '../services/timezoneService';

export type LocationSource = 'gps' | 'search' | 'map_click' | 'default' | 'ip_approximate';

interface WeatherContextType {
  currentLocation: CentralLocation;
  location: string;
  latitude: number;
  longitude: number;
  accuracy: number | null;
  locationSource: LocationSource;
  gpsStatus: GpsStatus;
  gpsError: string | null;
  isFollowingLocation: boolean;
  timezone: string;
  timezoneAbbreviation: string;
  localTimeStr: string;
  language: LanguageCode;
  tempUnit: 'celsius' | 'fahrenheit';
  windUnit: 'kmh' | 'ms';
  weather: CurrentWeather | null;
  forecast: ForecastData | null;
  alerts: AlertsData | null;
  isLoading: boolean;
  error: string | null;
  isDemoMode: boolean;
  setLocation: (loc: string, lat?: number, lon?: number) => void;
  setCoordinates: (lat: number, lon: number, source: LocationSource, customName?: string) => Promise<void>;
  useMyLocation: () => Promise<void>;
  toggleFollowLocation: () => void;
  startWatchingLocation: () => void;
  stopWatchingLocation: () => void;
  setLanguage: (lang: LanguageCode) => void;
  setTempUnit: (unit: 'celsius' | 'fahrenheit') => void;
  setWindUnit: (unit: 'kmh' | 'ms') => void;
  toggleDemoMode: () => void;
  refreshWeather: () => Promise<void>;
  t: (key: string) => string;
  translateCondition: (condition: string) => string;
  formatTemp: (celsius: number) => string;
  formatWind: (kmh: number) => string;
  formatHour: (isoTimeStr: string) => string;
  formatDate: (isoDateStr: string) => string;
  formatUpdated: (updatedAtStr?: string) => string;
}

const WeatherContext = createContext<WeatherContextType | undefined>(undefined);

export const WeatherProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Central Location Object (Section 2)
  const [currentLocation, setCurrentLocation] = useState<CentralLocation>(() => {
    const savedLoc = localStorage.getItem('weathergpt_location');
    const savedLat = localStorage.getItem('weathergpt_lat');
    const savedLon = localStorage.getItem('weathergpt_lon');
    const savedSource = (localStorage.getItem('weathergpt_source') as LocationSource) || 'default';
    const savedAcc = localStorage.getItem('weathergpt_accuracy');
    const savedDist = localStorage.getItem('weathergpt_district') || undefined;
    const savedState = localStorage.getItem('weathergpt_state') || 'Andhra Pradesh';
    const savedCountry = localStorage.getItem('weathergpt_country') || 'India';

    if (savedLoc && savedLat && savedLon) {
      return {
        latitude: parseFloat(savedLat),
        longitude: parseFloat(savedLon),
        accuracy: savedAcc ? parseFloat(savedAcc) : null,
        name: savedLoc,
        city: savedLoc.split(',')[0].trim(),
        district: savedDist,
        state: savedState,
        country: savedCountry,
        timezone: localStorage.getItem('weathergpt_timezone') || 'Asia/Kolkata',
        source: savedSource === 'gps' ? 'gps' : 'search',
        timestamp: new Date().toISOString()
      };
    }

    // Default initial location before GPS permission or search
    return {
      latitude: 16.3067,
      longitude: 80.4365,
      accuracy: null,
      name: 'Guntur, Andhra Pradesh',
      city: 'Guntur',
      district: 'Guntur District',
      state: 'Andhra Pradesh',
      country: 'India',
      timezone: 'Asia/Kolkata',
      source: 'default',
      timestamp: new Date().toISOString()
    };
  });

  const [gpsStatus, setGpsStatus] = useState<GpsStatus>('idle');
  const [gpsError, setGpsError] = useState<string | null>(null);
  const [isFollowingLocation, setIsFollowingLocation] = useState<boolean>(true);

  const [timezone, setTimezone] = useState<string>(() => {
    return localStorage.getItem('weathergpt_timezone') || 'Asia/Kolkata';
  });

  const [timezoneAbbreviation, setTimezoneAbbreviation] = useState<string>(() => {
    return localStorage.getItem('weathergpt_tz_abbr') || 'IST';
  });

  const [language, setLanguageState] = useState<LanguageCode>(() => {
    return (localStorage.getItem('weathergpt_language') as LanguageCode) || 'en';
  });

  const [localTimeStr, setLocalTimeStr] = useState<string>(() => {
    return formatLocalTimeWithAbbr(new Date(), 'Asia/Kolkata', 'IST', 'en');
  });

  // Live 1-second clock ticking in the selected location's timezone & language (no API requests)
  useEffect(() => {
    const updateClock = () => {
      setLocalTimeStr(formatLocalTimeWithAbbr(new Date(), timezone, timezoneAbbreviation, language));
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, [timezone, timezoneAbbreviation, language]);

  const [tempUnit, setTempUnitState] = useState<'celsius' | 'fahrenheit'>(() => {
    return (localStorage.getItem('weathergpt_temp_unit') as any) || 'celsius';
  });

  const [windUnit, setWindUnitState] = useState<'kmh' | 'ms'>(() => {
    return (localStorage.getItem('weathergpt_wind_unit') as any) || 'kmh';
  });

  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);
  const [weather, setWeather] = useState<CurrentWeather | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [alerts, setAlerts] = useState<AlertsData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [watchId, setWatchId] = useState<number | null>(null);
  const lastWeatherFetchCoords = useRef<{ lat: number; lon: number; time: number }>({
    lat: 16.3067,
    lon: 80.4365,
    time: Date.now()
  });

  const fetchWeatherData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [wData, fData, aData] = await Promise.all([
        api.getCurrentWeather(currentLocation.name, currentLocation.latitude, currentLocation.longitude),
        api.getForecast(currentLocation.name, 7, currentLocation.latitude, currentLocation.longitude),
        api.getAlerts(currentLocation.name, currentLocation.latitude, currentLocation.longitude),
      ]);
      setWeather(wData);
      setForecast(fData);
      setAlerts(aData);

      console.log('[GPS PIPELINE] WEATHER UPDATED:', {
        location: currentLocation.name,
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        temperature: wData?.temperature,
        precipitation: wData?.precipitation
      });

      if (wData?.timezone || fData?.timezone) {
        const tz = wData?.timezone || fData?.timezone || 'Asia/Kolkata';
        const abbr = wData?.timezone_abbreviation || fData?.timezone_abbreviation || getTimezoneAbbreviation(tz);
        setTimezone(tz);
        setTimezoneAbbreviation(abbr);
        localStorage.setItem('weathergpt_timezone', tz);
        localStorage.setItem('weathergpt_tz_abbr', abbr);
      }

      lastWeatherFetchCoords.current = { lat: currentLocation.latitude, lon: currentLocation.longitude, time: Date.now() };
    } catch (err: any) {
      console.error('Error loading weather data:', err);
      setError(err.message || 'Unable to retrieve weather data.');
    } finally {
      setIsLoading(false);
    }
  }, [currentLocation.name, currentLocation.latitude, currentLocation.longitude]);

  useEffect(() => {
    fetchWeatherData();
  }, [fetchWeatherData]);

  // Set location from search or manual selection
  const setLocation = (loc: string, lat?: number, lon?: number) => {
    const newLat = lat !== undefined ? lat : currentLocation.latitude;
    const newLon = lon !== undefined ? lon : currentLocation.longitude;
    const cleanName = loc.split(',')[0].trim();

    const newLocation: CentralLocation = {
      latitude: newLat,
      longitude: newLon,
      accuracy: null,
      name: loc,
      city: cleanName,
      source: 'search',
      timestamp: new Date().toISOString()
    };

    setCurrentLocation(newLocation);
    localStorage.setItem('weathergpt_location', loc);
    localStorage.setItem('weathergpt_lat', newLat.toString());
    localStorage.setItem('weathergpt_lon', newLon.toString());
    localStorage.setItem('weathergpt_source', 'search');
    localStorage.removeItem('weathergpt_accuracy');
  };

  // Set exact coordinates (from map click or GPS) with reverse geocoding
  const setCoordinates = async (
    lat: number,
    lon: number,
    source: LocationSource,
    customName?: string
  ) => {
    let resolvedName = customName || `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`;
    let city = '';
    let district = '';
    let state = '';
    let country = 'India';

    try {
      const geo = await api.reverseGeocode(lat, lon);
      if (geo && geo.name) {
        resolvedName = geo.display_name || geo.name;
        city = geo.city || geo.name;
        district = geo.district || '';
        state = geo.state || '';
        country = geo.country || 'India';
      }
    } catch (err) {
      console.warn('Reverse geocode error in setCoordinates:', err);
    }

    const newLoc: CentralLocation = {
      latitude: lat,
      longitude: lon,
      accuracy: source === 'gps' ? currentLocation.accuracy : null,
      name: resolvedName,
      city: city || resolvedName.split(',')[0].trim(),
      district: district,
      state: state,
      country: country,
      timezone: currentLocation.timezone,
      source: source === 'gps' ? 'gps' : 'search',
      timestamp: new Date().toISOString()
    };

    setCurrentLocation(newLoc);
    localStorage.setItem('weathergpt_location', resolvedName);
    localStorage.setItem('weathergpt_lat', lat.toString());
    localStorage.setItem('weathergpt_lon', lon.toString());
    localStorage.setItem('weathergpt_source', newLoc.source);
  };

  // One-time Live GPS Location Request with high accuracy (Section 1, 9, 26)
  const useMyLocation = async () => {
    console.log('[GPS PIPELINE] GPS REQUEST STARTED');
    setGpsStatus('loading');
    setGpsError(null);
    try {
      const pos = await locationService.getCurrentLocation();
      console.log('[GPS PIPELINE] GPS RESULT:', {
        latitude: pos.latitude,
        longitude: pos.longitude,
        accuracy: pos.accuracy,
        timestamp: pos.timestamp
      });

      setGpsStatus('granted');

      console.log('[GPS PIPELINE] REVERSE GEOCODING:', {
        latitude: pos.latitude,
        longitude: pos.longitude
      });

      let geo: any = null;
      try {
        geo = await api.reverseGeocode(pos.latitude, pos.longitude);
      } catch (err) {
        console.warn('Reverse geocoding error:', err);
      }

      console.log('[GPS PIPELINE] REVERSE GEOCODING RESULT:', geo);

      const placeName = geo?.name || geo?.display_name || `${pos.latitude.toFixed(4)}°, ${pos.longitude.toFixed(4)}°`;
      const district = geo?.district || '';
      const state = geo?.state || '';
      const country = geo?.country || 'India';
      const city = geo?.city || placeName;

      const newLocation: CentralLocation = {
        latitude: pos.latitude,
        longitude: pos.longitude,
        accuracy: pos.accuracy,
        name: placeName,
        city: city,
        district: district,
        state: state,
        country: country,
        timezone: timezone || 'Asia/Kolkata',
        source: 'gps',
        timestamp: new Date(pos.timestamp).toISOString()
      };

      setCurrentLocation(newLocation);
      console.log('[GPS PIPELINE] CENTRAL LOCATION UPDATED:', newLocation);

      localStorage.setItem('weathergpt_location', placeName);
      localStorage.setItem('weathergpt_lat', pos.latitude.toString());
      localStorage.setItem('weathergpt_lon', pos.longitude.toString());
      localStorage.setItem('weathergpt_source', 'gps');
      localStorage.setItem('weathergpt_accuracy', pos.accuracy.toString());
      if (district) localStorage.setItem('weathergpt_district', district);
      if (state) localStorage.setItem('weathergpt_state', state);
      if (country) localStorage.setItem('weathergpt_country', country);

      console.log('[GPS PIPELINE] MAP UPDATED:', {
        latitude: pos.latitude,
        longitude: pos.longitude,
        name: placeName
      });
    } catch (err: any) {
      console.error('[GPS PIPELINE] GPS acquisition error:', err);
      setGpsStatus('denied');
      setGpsError('GPS permission is unavailable.');
    }
  };

  // Continuous watchPosition with distance/time throttling (Section 10)
  const startWatchingLocation = () => {
    if (watchId !== null) return;
    const id = locationService.watchCurrentLocation(
      async (pos) => {
        setGpsStatus('granted');

        const now = Date.now();
        const dist = locationService.calculateDistance(
          lastWeatherFetchCoords.current.lat,
          lastWeatherFetchCoords.current.lon,
          pos.latitude,
          pos.longitude
        );
        const timeDiff = now - lastWeatherFetchCoords.current.time;

        // Only update central state and weather if device moved significantly (> 150m or > 5 min)
        if (dist > 150 || timeDiff > 300000) {
          let geo: any = null;
          try {
            geo = await api.reverseGeocode(pos.latitude, pos.longitude);
          } catch (e) {
            console.warn('Watch reverse geocode error:', e);
          }

          const placeName = geo?.name || geo?.display_name || `${pos.latitude.toFixed(4)}°, ${pos.longitude.toFixed(4)}°`;
          const updatedLoc: CentralLocation = {
            latitude: pos.latitude,
            longitude: pos.longitude,
            accuracy: pos.accuracy,
            name: placeName,
            city: geo?.city || placeName,
            district: geo?.district || '',
            state: geo?.state || '',
            country: geo?.country || 'India',
            timezone: timezone || 'Asia/Kolkata',
            source: 'gps',
            timestamp: new Date(pos.timestamp).toISOString()
          };

          setCurrentLocation(updatedLoc);
          lastWeatherFetchCoords.current = { lat: pos.latitude, lon: pos.longitude, time: now };
          localStorage.setItem('weathergpt_location', placeName);
          localStorage.setItem('weathergpt_lat', pos.latitude.toString());
          localStorage.setItem('weathergpt_lon', pos.longitude.toString());
          localStorage.setItem('weathergpt_source', 'gps');
        }
      },
      (err) => {
        setGpsError(err.message || 'GPS tracking error');
      }
    );
    setWatchId(id);
  };

  const stopWatchingLocation = () => {
    if (watchId !== null) {
      locationService.stopWatchingLocation(watchId);
      setWatchId(null);
    }
  };

  const toggleFollowLocation = () => {
    setIsFollowingLocation((prev) => !prev);
  };

  const setLanguage = (lang: LanguageCode) => {
    setLanguageState(lang);
    localStorage.setItem('weathergpt_language', lang);
    const token = localStorage.getItem('weathergpt_token');
    if (token) {
      api.updatePreferences({ language: lang }, token).catch(err => {
        console.warn('Sync language preference error:', err);
      });
    }
  };

  const setTempUnit = (unit: 'celsius' | 'fahrenheit') => {
    setTempUnitState(unit);
    localStorage.setItem('weathergpt_temp_unit', unit);
  };

  const setWindUnit = (unit: 'kmh' | 'ms') => {
    setWindUnitState(unit);
    localStorage.setItem('weathergpt_wind_unit', unit);
  };

  const toggleDemoMode = () => {
    setIsDemoMode((prev) => !prev);
  };

  const t = (key: string): string => {
    const langDict = translations[language] || translations['en'];
    return langDict[key] || translations['en'][key] || key;
  };

  const formatTemp = (celsius: number): string => {
    if (tempUnit === 'fahrenheit') {
      const f = (celsius * 9) / 5 + 32;
      return `${Math.round(f)}°F`;
    }
    return `${Math.round(celsius)}°C`;
  };

  const formatWind = (kmh: number): string => {
    if (windUnit === 'ms') {
      const ms = kmh / 3.6;
      return `${ms.toFixed(1)} m/s`;
    }
    return `${kmh.toFixed(1)} km/h`;
  };

  const formatHour = useCallback((isoTimeStr: string): string => {
    return tzFormatHour(isoTimeStr, timezone, language);
  }, [timezone, language]);

  const formatDate = useCallback((isoDateStr: string): string => {
    return tzFormatDate(isoDateStr, timezone, language);
  }, [timezone, language]);

  const formatUpdated = useCallback((updatedAtStr?: string): string => {
    return tzFormatUpdated(updatedAtStr, timezone, timezoneAbbreviation, language);
  }, [timezone, timezoneAbbreviation, language]);

  const translateConditionHelper = useCallback((cond: string): string => {
    return translateCondition(cond, language);
  }, [language]);

  return (
    <WeatherContext.Provider
      value={{
        currentLocation,
        location: currentLocation.name,
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        accuracy: currentLocation.accuracy,
        locationSource: currentLocation.source,
        gpsStatus,
        gpsError,
        isFollowingLocation,
        timezone,
        timezoneAbbreviation,
        localTimeStr,
        language,
        tempUnit,
        windUnit,
        weather,
        forecast,
        alerts,
        isLoading,
        error,
        isDemoMode,
        setLocation,
        setCoordinates,
        useMyLocation,
        toggleFollowLocation,
        startWatchingLocation,
        stopWatchingLocation,
        setLanguage,
        setTempUnit,
        setWindUnit,
        toggleDemoMode,
        refreshWeather: fetchWeatherData,
        t,
        translateCondition: translateConditionHelper,
        formatTemp,
        formatWind,
        formatHour,
        formatDate,
        formatUpdated,
      }}
    >
      {children}
    </WeatherContext.Provider>
  );
};

export const useWeather = (): WeatherContextType => {
  const context = useContext(WeatherContext);
  if (!context) {
    throw new Error('useWeather must be used within a WeatherProvider');
  }
  return context;
};
