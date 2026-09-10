/**
 * WeatherGPT Timezone Service
 * Strict timezone conversions using native Intl.DateTimeFormat without relying on the client's computer clock.
 */

// Well-known IANA timezone canonical abbreviations with DST awareness
export const KNOWN_TIMEZONE_ABBRS: Record<string, { standard: string; daylight: string }> = {
  'Asia/Kolkata': { standard: 'IST', daylight: 'IST' },
  'Asia/Calcutta': { standard: 'IST', daylight: 'IST' },
  'Europe/London': { standard: 'GMT', daylight: 'BST' },
  'America/New_York': { standard: 'EST', daylight: 'EDT' },
  'America/Chicago': { standard: 'CST', daylight: 'CDT' },
  'America/Denver': { standard: 'MST', daylight: 'MDT' },
  'America/Los_Angeles': { standard: 'PST', daylight: 'PDT' },
  'Asia/Tokyo': { standard: 'JST', daylight: 'JST' },
  'Australia/Sydney': { standard: 'AEST', daylight: 'AEDT' },
  'Asia/Dubai': { standard: 'GST', daylight: 'GST' },
  'Asia/Singapore': { standard: 'SGT', daylight: 'SGT' },
  'Europe/Paris': { standard: 'CET', daylight: 'CEST' },
  'Europe/Berlin': { standard: 'CET', daylight: 'CEST' },
  'Asia/Bangkok': { standard: 'ICT', daylight: 'ICT' },
  'Asia/Hong_Kong': { standard: 'HKT', daylight: 'HKT' },
  'America/Toronto': { standard: 'EST', daylight: 'EDT' },
  'America/Vancouver': { standard: 'PST', daylight: 'PDT' },
  'America/Sao_Paulo': { standard: 'BRT', daylight: 'BRT' },
  'Africa/Johannesburg': { standard: 'SAST', daylight: 'SAST' }
};

/**
 * Validates whether a timezone string is a recognized IANA identifier
 */
export function isValidTimezone(timezone?: string): boolean {
  if (!timezone) return false;
  try {
    Intl.DateTimeFormat(undefined, { timeZone: timezone });
    return true;
  } catch {
    return false;
  }
}

/**
 * Returns the abbreviation (e.g. IST, BST, EDT, JST) for a given timezone and date
 */
export function getTimezoneAbbreviation(timezone: string = 'Asia/Kolkata', date: Date = new Date()): string {
  const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';

  // Check known map first
  const known = KNOWN_TIMEZONE_ABBRS[safeTz];
  if (known) {
    try {
      // Check if DST is active in this timezone
      const parts = new Intl.DateTimeFormat('en-US', {
        timeZone: safeTz,
        timeZoneName: 'short'
      }).formatToParts(date);
      const tzPart = parts.find(p => p.type === 'timeZoneName')?.value;
      if (tzPart && (tzPart.includes('DT') || tzPart === known.daylight)) {
        return known.daylight;
      }
      return known.daylight || known.standard;
    } catch {
      return known.daylight || known.standard;
    }
  }

  // Fallback to Intl extraction
  try {
    const parts = new Intl.DateTimeFormat('en-US', {
      timeZone: safeTz,
      timeZoneName: 'short'
    }).formatToParts(date);
    const tzPart = parts.find(p => p.type === 'timeZoneName')?.value;
    if (tzPart && !tzPart.startsWith('GMT+') && !tzPart.startsWith('GMT-') && !tzPart.startsWith('UTC')) {
      return tzPart;
    }
    return tzPart || 'UTC';
  } catch {
    return 'UTC';
  }
}

export const LOCALE_MAP: Record<string, string> = {
  en: 'en-US',
  hi: 'hi-IN',
  te: 'te-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  mr: 'mr-IN',
  bn: 'bn-IN',
};

export function getLocaleForLang(lang?: string): string {
  if (!lang) return 'en-US';
  return LOCALE_MAP[lang] || 'en-US';
}

/**
 * Formats a given Date into the location's local time string (e.g. "7:58 PM")
 */
export function formatLocalTime(
  dateOrTimestamp: Date | string | number = new Date(),
  timezone: string = 'Asia/Kolkata',
  includeSeconds: boolean = false,
  lang: string = 'en'
): string {
  const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';
  const d = typeof dateOrTimestamp === 'string' || typeof dateOrTimestamp === 'number'
    ? new Date(dateOrTimestamp)
    : dateOrTimestamp;

  const validDate = isNaN(d.getTime()) ? new Date() : d;
  const locale = getLocaleForLang(lang);

  return new Intl.DateTimeFormat(locale, {
    timeZone: safeTz,
    hour: 'numeric',
    minute: '2-digit',
    second: includeSeconds ? '2-digit' : undefined,
    hour12: true
  }).format(validDate);
}

/**
 * Formats a given Date into local time with abbreviation (e.g. "7:58 PM IST")
 */
export function formatLocalTimeWithAbbr(
  dateOrTimestamp: Date | string | number = new Date(),
  timezone: string = 'Asia/Kolkata',
  providedAbbr?: string,
  lang: string = 'en'
): string {
  const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';
  const timeStr = formatLocalTime(dateOrTimestamp, safeTz, false, lang);
  const abbr = providedAbbr || getTimezoneAbbreviation(safeTz);
  return `${timeStr} ${abbr}`;
}

/**
 * Formats an hourly forecast timestamp into "7 PM", "8 PM", "12 AM", etc.
 * Handles ISO strings like "2026-09-09T19:00" or raw hour numbers.
 */
export function formatLocalHour(isoTimeStr: string, timezone: string = 'Asia/Kolkata', lang: string = 'en'): string {
  if (!isoTimeStr) return '';

  // If format is "2026-09-09T19:00" or "2026-09-09 19:00"
  if (isoTimeStr.includes('T') || (isoTimeStr.includes('-') && isoTimeStr.includes(':'))) {
    try {
      const d = new Date(isoTimeStr);
      if (!isNaN(d.getTime())) {
        const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';
        const locale = getLocaleForLang(lang);
        return new Intl.DateTimeFormat(locale, {
          timeZone: safeTz,
          hour: 'numeric',
          hour12: true
        }).format(d);
      }
    } catch {
      // fallback to manual parse below
    }

    const timePart = isoTimeStr.split(/[T ]/)[1];
    if (timePart) {
      const hourNum = parseInt(timePart.split(':')[0], 10);
      if (!isNaN(hourNum)) {
        const ampm = hourNum < 12 || hourNum === 24 ? 'AM' : 'PM';
        const h12 = hourNum % 12 === 0 ? 12 : hourNum % 12;
        return `${h12} ${ampm}`;
      }
    }
  }

  // If format is "19:00"
  if (isoTimeStr.includes(':') && !isoTimeStr.includes('-')) {
    const hourNum = parseInt(isoTimeStr.split(':')[0], 10);
    if (!isNaN(hourNum)) {
      const ampm = hourNum < 12 || hourNum === 24 ? 'AM' : 'PM';
      const h12 = hourNum % 12 === 0 ? 12 : hourNum % 12;
      return `${h12} ${ampm}`;
    }
  }

  // Fallback parse as ISO date
  try {
    const d = new Date(isoTimeStr);
    if (!isNaN(d.getTime())) {
      const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';
      const locale = getLocaleForLang(lang);
      return new Intl.DateTimeFormat(locale, {
        timeZone: safeTz,
        hour: 'numeric',
        hour12: true
      }).format(d);
    }
  } catch {
    // fallback
  }

  return isoTimeStr;
}

/**
 * Formats a forecast calendar date into "Wed, Sep 9", "Tue, Sep 10", etc.
 */
export function formatLocalDate(isoDateStr: string, timezone: string = 'Asia/Kolkata', lang: string = 'en'): string {
  if (!isoDateStr) return '';
  const locale = getLocaleForLang(lang);

  // Normalize "YYYY-MM-DD" without timezone skew
  const parts = isoDateStr.split('-');
  if (parts.length === 3) {
    const y = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    const dateObj = new Date(Date.UTC(y, m, d, 12, 0, 0));
    return new Intl.DateTimeFormat(locale, {
      timeZone: 'UTC',
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    }).format(dateObj);
  }

  try {
    const dateObj = new Date(isoDateStr);
    if (!isNaN(dateObj.getTime())) {
      const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';
      return new Intl.DateTimeFormat(locale, {
        timeZone: safeTz,
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      }).format(dateObj);
    }
  } catch {
    // ignore
  }

  return isoDateStr;
}

/**
 * Formats the weather "Updated" timestamp into clean local format like "Sep 9, 2026, 7:46 PM IST"
 */
export function formatUpdatedTime(
  updatedAtStr?: string,
  timezone: string = 'Asia/Kolkata',
  abbr?: string,
  lang: string = 'en'
): string {
  if (!updatedAtStr) return '';

  // If it already has an AM/PM local format like "Sep 09, 2026, 8:01 PM IST"
  if (updatedAtStr.includes('AM') || updatedAtStr.includes('PM')) {
    return updatedAtStr;
  }

  // If it is in "YYYY-MM-DD HH:MM:SS UTC" format
  if (updatedAtStr.includes('UTC')) {
    const cleanStr = updatedAtStr.replace(' UTC', 'Z').replace(' ', 'T');
    const d = new Date(cleanStr);
    if (!isNaN(d.getTime())) {
      const safeTz = isValidTimezone(timezone) ? timezone : 'Asia/Kolkata';
      const timeStr = formatLocalTime(d, safeTz, false, lang);
      const locale = getLocaleForLang(lang);
      const dateStr = new Intl.DateTimeFormat(locale, {
        timeZone: safeTz,
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(d);
      const tzAbbr = abbr || getTimezoneAbbreviation(safeTz, d);
      return `${dateStr}, ${timeStr} ${tzAbbr}`;
    }
  }

  return updatedAtStr;
}
