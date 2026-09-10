import type { CurrentWeather } from '../types/index.ts';

export type WeatherVisualCondition =
  | 'clear'
  | 'partly-cloudy'
  | 'cloudy'
  | 'overcast'
  | 'drizzle'
  | 'rain'
  | 'heavy-rain'
  | 'thunderstorm'
  | 'fog'
  | 'snow'
  | 'unknown';

export type WeatherIntensity = 'light' | 'moderate' | 'heavy';

export interface WeatherVisualState {
  condition: WeatherVisualCondition;
  intensity: WeatherIntensity;
  isNight: boolean;
  animation: 'sun-glow' | 'moon-stars' | 'clouds' | 'rain' | 'heavy-rain' | 'lightning' | 'fog' | 'snow' | 'none';
  backgroundType: string;
  conditionLabel: string;
  temperature: number | null;
  precipitation: number;
  windSpeed: number;
  cloudCover: number;
  timezone: string;
  localTimeStr: string;
  sunriseStr: string;
  sunsetStr: string;
  weatherCode: number | null;
}

/**
 * Parses time string like "06:14 AM", "18:30", "2026-09-10T06:14" into total minutes from midnight.
 */
export function parseTimeToMinutes(timeStr?: string): number | null {
  if (!timeStr) return null;
  try {
    const clean = timeStr.trim();
    
    // Check if ISO format e.g. 2026-09-10T06:14:00
    if (clean.includes('T')) {
      const timePart = clean.split('T')[1];
      const [h, m] = timePart.split(':');
      return parseInt(h, 10) * 60 + parseInt(m || '0', 10);
    }

    // Check 12-hour AM/PM format
    const isPM = /pm/i.test(clean);
    const isAM = /am/i.test(clean);
    const parts = clean.replace(/[^\d:]/g, '').split(':');
    if (parts.length >= 2) {
      let hours = parseInt(parts[0], 10);
      const minutes = parseInt(parts[1], 10);
      if (isPM && hours < 12) hours += 12;
      if (isAM && hours === 12) hours = 0;
      return hours * 60 + minutes;
    }
  } catch {
    return null;
  }
  return null;
}

/**
 * Calculates current time in minutes from midnight for the specified location timezone.
 * Uses Intl.DateTimeFormat so it respects the TARGET location timezone, NOT browser timezone.
 */
export function getLocalMinutesInTimezone(timezone: string): { minutes: number; formatted: string } {
  try {
    const now = new Date();
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone: timezone,
      hour: 'numeric',
      minute: 'numeric',
      hour12: false
    });
    const parts = formatter.formatToParts(now);
    const hStr = parts.find(p => p.type === 'hour')?.value || '12';
    const mStr = parts.find(p => p.type === 'minute')?.value || '00';
    const hour = parseInt(hStr, 10);
    const minute = parseInt(mStr, 10);

    const displayFormatter = new Intl.DateTimeFormat('en-US', {
      timeZone: timezone,
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    });

    return {
      minutes: hour * 60 + minute,
      formatted: displayFormatter.format(now)
    };
  } catch {
    const now = new Date();
    return {
      minutes: now.getHours() * 60 + now.getMinutes(),
      formatted: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  }
}

/**
 * Determines whether it is currently night at the target location.
 */
export function calculateIsNight(
  timezone: string,
  sunriseStr?: string,
  sunsetStr?: string,
  isDayFlag?: number
): { isNight: boolean; localTimeStr: string } {
  // If weather API explicitly provided is_day flag, check it
  if (isDayFlag !== undefined && isDayFlag !== null) {
    const { formatted } = getLocalMinutesInTimezone(timezone);
    return { isNight: isDayFlag === 0, localTimeStr: formatted };
  }

  const { minutes: currentMinutes, formatted } = getLocalMinutesInTimezone(timezone);

  const sunriseMinutes = parseTimeToMinutes(sunriseStr) ?? (6 * 60); // default 6:00 AM
  const sunsetMinutes = parseTimeToMinutes(sunsetStr) ?? (18 * 60 + 30); // default 6:30 PM

  // Night if before sunrise or after sunset
  let isNight = false;
  if (sunriseMinutes < sunsetMinutes) {
    isNight = currentMinutes < sunriseMinutes || currentMinutes >= sunsetMinutes;
  } else {
    // Polar or edge cases
    isNight = currentMinutes < sunriseMinutes && currentMinutes >= sunsetMinutes;
  }

  return { isNight, localTimeStr: formatted };
}

/**
 * Maps Open-Meteo WMO Weather Codes and weather conditions to a canonical condition and intensity.
 */
export function mapWmoCodeToCondition(
  wmoCode?: number | null,
  conditionText?: string,
  precipAmount?: number | null
): { condition: WeatherVisualCondition; intensity: WeatherIntensity } {
  const precip = precipAmount ?? 0;

  if (wmoCode !== undefined && wmoCode !== null) {
    switch (wmoCode) {
      // Clear
      case 0:
        return { condition: 'clear', intensity: 'light' };

      // Mainly Clear & Partly Cloudy
      case 1:
      case 2:
        return { condition: 'partly-cloudy', intensity: 'light' };

      // Overcast
      case 3:
        return { condition: 'overcast', intensity: 'moderate' };

      // Fog
      case 45:
      case 48:
        return { condition: 'fog', intensity: 'moderate' };

      // Drizzle
      case 51:
      case 53:
      case 55:
      case 56:
      case 57:
        return { condition: 'drizzle', intensity: 'light' };

      // Rain
      case 61:
        return { condition: 'rain', intensity: 'light' };
      case 63:
        return { condition: 'rain', intensity: 'moderate' };
      case 65:
        return { condition: 'heavy-rain', intensity: 'heavy' };
      case 66:
      case 67:
        return { condition: 'rain', intensity: 'moderate' };

      // Snow
      case 71:
        return { condition: 'snow', intensity: 'light' };
      case 73:
        return { condition: 'snow', intensity: 'moderate' };
      case 75:
      case 77:
        return { condition: 'snow', intensity: 'heavy' };

      // Showers
      case 80:
        return { condition: 'rain', intensity: 'light' };
      case 81:
        return { condition: 'rain', intensity: 'moderate' };
      case 82:
        return { condition: 'heavy-rain', intensity: 'heavy' };
      case 85:
      case 86:
        return { condition: 'snow', intensity: 'moderate' };

      // Thunderstorm
      case 95:
        return { condition: 'thunderstorm', intensity: 'moderate' };
      case 96:
      case 99:
        return { condition: 'thunderstorm', intensity: 'heavy' };

      default:
        break;
    }
  }

  // Fallback string matching on conditionText
  if (conditionText) {
    const text = conditionText.toLowerCase();

    if (text.includes('thunder') || text.includes('lightning') || text.includes('storm')) {
      return { condition: 'thunderstorm', intensity: text.includes('heavy') || precip > 5 ? 'heavy' : 'moderate' };
    }
    if (text.includes('heavy rain') || text.includes('torrential') || text.includes('downpour') || precip >= 7.6) {
      return { condition: 'heavy-rain', intensity: 'heavy' };
    }
    if (text.includes('drizzle')) {
      return { condition: 'drizzle', intensity: 'light' };
    }
    if (text.includes('rain') || text.includes('shower')) {
      return { condition: 'rain', intensity: precip >= 2.5 ? 'moderate' : 'light' };
    }
    if (text.includes('snow') || text.includes('blizzard') || text.includes('sleet')) {
      return { condition: 'snow', intensity: text.includes('heavy') ? 'heavy' : 'moderate' };
    }
    if (text.includes('fog') || text.includes('mist') || text.includes('haze')) {
      return { condition: 'fog', intensity: 'moderate' };
    }
    if (text.includes('overcast')) {
      return { condition: 'overcast', intensity: 'moderate' };
    }
    if (text.includes('cloud') || text.includes('partly')) {
      return { condition: text.includes('partly') ? 'partly-cloudy' : 'cloudy', intensity: 'light' };
    }
    if (text.includes('clear') || text.includes('sun')) {
      return { condition: 'clear', intensity: 'light' };
    }
  }

  return { condition: 'unknown', intensity: 'light' };
}

/**
 * Main Centralized Mapper: maps normalized weather object and location to WeatherVisualState.
 */
export function mapWeatherToVisualState(
  weather: CurrentWeather | null,
  location?: { timezone?: string; name?: string; latitude?: number; longitude?: number }
): WeatherVisualState {
  if (!weather) {
    return {
      condition: 'unknown',
      intensity: 'light',
      isNight: false,
      animation: 'none',
      backgroundType: 'neutral-ambient',
      conditionLabel: 'Weather Data Loading...',
      temperature: null,
      precipitation: 0,
      windSpeed: 0,
      cloudCover: 0,
      timezone: location?.timezone || 'Asia/Kolkata',
      localTimeStr: '--:--',
      sunriseStr: '06:00 AM',
      sunsetStr: '06:30 PM',
      weatherCode: null
    };
  }

  // 1. Resolve exact target timezone
  const tz = weather.timezone || location?.timezone || 'Asia/Kolkata';

  // 2. Day/Night detection using target location's timezone and sunrise/sunset
  const sunrise = weather.sunrise || '06:00 AM';
  const sunset = weather.sunset || '06:30 PM';
  const { isNight, localTimeStr } = calculateIsNight(
    tz,
    sunrise,
    sunset,
    (weather as any).is_day
  );

  // 3. Condition & Intensity mapping
  const wmoCode = weather.condition_code ?? null;
  const conditionStr = weather.condition || '';
  const precipVal = weather.precipitation ?? 0;
  const { condition, intensity } = mapWmoCodeToCondition(wmoCode, conditionStr, precipVal);

  // 4. Determine animation and backgroundType
  let animation: WeatherVisualState['animation'] = 'none';
  let bgType = 'neutral-ambient';

  switch (condition) {
    case 'clear':
      if (isNight) {
        animation = 'moon-stars';
        bgType = 'clear-night';
      } else {
        animation = 'sun-glow';
        bgType = 'sunny-day';
      }
      break;

    case 'partly-cloudy':
      animation = 'clouds';
      bgType = isNight ? 'partly-cloudy-night' : 'partly-cloudy-day';
      break;

    case 'cloudy':
    case 'overcast':
      animation = 'clouds';
      bgType = isNight ? 'cloudy-night' : (condition === 'overcast' ? 'overcast-day' : 'cloudy-day');
      break;

    case 'drizzle':
    case 'rain':
      animation = 'rain';
      bgType = isNight ? 'rain-night' : 'rain-day';
      break;

    case 'heavy-rain':
      animation = 'heavy-rain';
      bgType = isNight ? 'heavy-rain-night' : 'heavy-rain-day';
      break;

    case 'thunderstorm':
      animation = 'lightning';
      bgType = isNight ? 'thunderstorm-night' : 'thunderstorm-day';
      break;

    case 'fog':
      animation = 'fog';
      bgType = isNight ? 'fog-night' : 'fog-day';
      break;

    case 'snow':
      animation = 'snow';
      bgType = isNight ? 'snow-night' : 'snow-day';
      break;

    default:
      animation = isNight ? 'moon-stars' : 'none';
      bgType = isNight ? 'neutral-night' : 'neutral-ambient';
      break;
  }

  // 5. Cloud cover estimation
  let estimatedCloudCover = 10;
  if (condition === 'clear') estimatedCloudCover = 5;
  else if (condition === 'partly-cloudy') estimatedCloudCover = 40;
  else if (condition === 'cloudy') estimatedCloudCover = 75;
  else if (condition === 'overcast' || condition === 'rain' || condition === 'heavy-rain' || condition === 'thunderstorm') estimatedCloudCover = 95;
  else if (condition === 'fog') estimatedCloudCover = 80;

  return {
    condition,
    intensity,
    isNight,
    animation,
    backgroundType: bgType,
    conditionLabel: conditionStr || condition.replace('-', ' ').toUpperCase(),
    temperature: weather.temperature,
    precipitation: precipVal,
    windSpeed: weather.wind_speed ?? 0,
    cloudCover: estimatedCloudCover,
    timezone: tz,
    localTimeStr,
    sunriseStr: sunrise,
    sunsetStr: sunset,
    weatherCode: wmoCode
  };
}
