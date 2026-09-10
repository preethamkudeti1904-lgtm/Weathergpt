/**
 * windService.ts
 * Meteorological Wind Service for WeatherGPT
 * Provides normalized real-time and forecast wind vectors, Beaufort classifications,
 * degree conversions, and timezone-aware hourly projections.
 */

import { api } from './api';
import { CurrentWeather, ForecastData } from '../types';

export interface WindPoint {
  windSpeed: number | null; // km/h
  windDirection: number | null; // degrees (0-360)
  windDirectionCardinal: string | null; // e.g. "NE", "E"
  windGust: number | null; // km/h
  timestamp: string; // ISO or formatted
  beaufortScale: BeaufortLevel;
}

export interface NormalizedWindData {
  latitude: number;
  longitude: number;
  locationName: string;
  timezone: string;
  current: WindPoint;
  hourly: WindPoint[];
  source: string;
  updatedAt: string;
}

export type BeaufortScaleCategory = 'calm' | 'light_breeze' | 'moderate_breeze' | 'strong_wind' | 'very_strong_wind';

export interface BeaufortLevel {
  category: BeaufortScaleCategory;
  labelKey: string;
  label: string;
  minKmh: number;
  maxKmh: number | null;
  color: string;
  description: string;
}

export const BEAUFORT_LEVELS: BeaufortLevel[] = [
  {
    category: 'calm',
    labelKey: 'calm',
    label: 'Calm',
    minKmh: 0,
    maxKmh: 5,
    color: '#10b981', // emerald-500
    description: 'Smoke rises vertically. Sea like a mirror (< 5 km/h)'
  },
  {
    category: 'light_breeze',
    labelKey: 'light_breeze',
    label: 'Light',
    minKmh: 5,
    maxKmh: 19,
    color: '#06b6d4', // cyan-500
    description: 'Leaves rustle, wind felt on face (5 - 19 km/h)'
  },
  {
    category: 'moderate_breeze',
    labelKey: 'moderate_breeze',
    label: 'Moderate',
    minKmh: 20,
    maxKmh: 38,
    color: '#3b82f6', // blue-500
    description: 'Small branches move, dust raised (20 - 38 km/h)'
  },
  {
    category: 'strong_wind',
    labelKey: 'strong_wind',
    label: 'Strong',
    minKmh: 39,
    maxKmh: 61,
    color: '#f59e0b', // amber-500
    description: 'Large branches in motion, umbrellas used with difficulty (39 - 61 km/h)'
  },
  {
    category: 'very_strong_wind',
    labelKey: 'very_strong_wind',
    label: 'Very Strong',
    minKmh: 62,
    maxKmh: null,
    color: '#ef4444', // red-500
    description: 'Whole trees in motion, high waves, gale force (>= 62 km/h)'
  }
];

/**
 * Converts meteorological degrees (0-360) to 16-point cardinal compass string
 */
export function degreesToCardinal(deg: number | null | undefined): string {
  if (deg === null || deg === undefined || isNaN(deg)) return '--';
  const normalized = ((deg % 360) + 360) % 360;
  const cardinals = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const idx = Math.round(normalized / 22.5) % 16;
  return cardinals[idx];
}

/**
 * Returns the Beaufort category based on speed in km/h
 */
export function getBeaufortLevel(kmh: number | null | undefined): BeaufortLevel {
  if (kmh === null || kmh === undefined || isNaN(kmh) || kmh < 0) {
    return BEAUFORT_LEVELS[0];
  }
  if (kmh < 5) return BEAUFORT_LEVELS[0]; // Calm
  if (kmh <= 19) return BEAUFORT_LEVELS[1]; // Light
  if (kmh <= 38) return BEAUFORT_LEVELS[2]; // Moderate
  if (kmh <= 61) return BEAUFORT_LEVELS[3]; // Strong
  return BEAUFORT_LEVELS[4]; // Very Strong
}

/**
 * In-memory cache for wind data keyed by `lat:lon:provider`
 */
const windCache = new Map<string, { data: NormalizedWindData; expiresAt: number }>();
const CACHE_TTL_MS = 3 * 60 * 1000; // 3 minutes

export const windService = {
  /**
   * Fetches real meteorological wind data from the centralized backend service
   */
  async getWindData(
    lat: number,
    lon: number,
    locationName: string,
    timezone?: string
  ): Promise<NormalizedWindData> {
    const cacheKey = `${lat.toFixed(4)}:${lon.toFixed(4)}:open_meteo`;
    const cached = windCache.get(cacheKey);
    const now = Date.now();

    if (cached && cached.expiresAt > now) {
      return cached.data;
    }

    try {
      // Fetch real forecast which includes current and hourly wind vectors
      const forecast: ForecastData = await api.getForecast(locationName, 2, lat, lon);

      const curr = forecast.current;
      const currentWindSpeed = curr?.wind_speed !== undefined ? curr.wind_speed : null;
      const currentWindDir = curr?.wind_direction !== undefined ? curr.wind_direction : null;
      const currentGust = curr?.wind_gusts !== undefined ? curr.wind_gusts : (currentWindSpeed !== null ? Math.round(currentWindSpeed * 1.35 * 10) / 10 : null);

      const currentPoint: WindPoint = {
        windSpeed: currentWindSpeed,
        windDirection: currentWindDir,
        windDirectionCardinal: curr?.wind_direction_cardinal || degreesToCardinal(currentWindDir),
        windGust: currentGust,
        timestamp: curr?.updated_at || new Date().toISOString(),
        beaufortScale: getBeaufortLevel(currentWindSpeed)
      };

      const hourlyPoints: WindPoint[] = (forecast.hourly || []).slice(0, 24).map((h) => {
        const speed = h.wind_speed !== undefined ? h.wind_speed : null;
        const dir = h.wind_direction !== undefined && h.wind_direction !== null ? h.wind_direction : currentWindDir;
        const gust = h.wind_gusts !== undefined && h.wind_gusts !== null ? h.wind_gusts : (speed !== null ? Math.round(speed * 1.35 * 10) / 10 : null);
        return {
          windSpeed: speed,
          windDirection: dir,
          windDirectionCardinal: h.wind_direction_cardinal || degreesToCardinal(dir),
          windGust: gust,
          timestamp: h.time,
          beaufortScale: getBeaufortLevel(speed)
        };
      });

      const normalized: NormalizedWindData = {
        latitude: lat,
        longitude: lon,
        locationName: forecast.location_name || locationName,
        timezone: forecast.timezone || timezone || 'UTC',
        current: currentPoint,
        hourly: hourlyPoints,
        source: forecast.source || 'Open-Meteo High-Resolution Surface Wind Analysis',
        updatedAt: forecast.updated_at || new Date().toISOString()
      };

      // Dev-only diagnostic logging
      if ((import.meta as any)?.env?.DEV) {
        console.log(
          `[WindMap] lat: ${lat.toFixed(4)}, lon: ${lon.toFixed(4)}, ` +
          `direction: ${currentPoint.windDirection !== null ? currentPoint.windDirection + '°' : 'null'}, ` +
          `speed: ${currentPoint.windSpeed !== null ? currentPoint.windSpeed + ' km/h' : 'null'}, ` +
          `gust: ${currentPoint.windGust !== null ? currentPoint.windGust + ' km/h' : 'null'}, ` +
          `timestamp: ${currentPoint.timestamp}`
        );
      }

      windCache.set(cacheKey, { data: normalized, expiresAt: now + CACHE_TTL_MS });
      return normalized;
    } catch (err) {
      console.error('[WindMap] Failed to fetch wind data:', err);
      throw err;
    }
  },

  /**
   * Manually invalidate cached wind data for a given location
   */
  invalidateCache(lat?: number, lon?: number) {
    if (lat !== undefined && lon !== undefined) {
      const cacheKey = `${lat.toFixed(4)}:${lon.toFixed(4)}:open_meteo`;
      windCache.delete(cacheKey);
    } else {
      windCache.clear();
    }
  }
};
