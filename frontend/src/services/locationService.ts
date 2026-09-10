export interface GpsLocationResult {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: number;
}

export type GpsStatus = 'idle' | 'loading' | 'granted' | 'denied' | 'unavailable';

const GPS_OPTIONS: PositionOptions = {
  enableHighAccuracy: true,
  timeout: 15000,
  maximumAge: 0,
};

export const locationService = {
  /**
   * Retrieves high-accuracy one-time GPS coordinates via browser Geolocation API
   */
  getCurrentLocation: (): Promise<GpsLocationResult> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser.'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: Math.round(position.coords.accuracy),
            timestamp: position.timestamp,
          });
        },
        (error) => {
          let message = 'Unable to determine your location.';
          if (error.code === error.PERMISSION_DENIED) {
            message = 'Location permission was denied by the browser.';
          } else if (error.code === error.POSITION_UNAVAILABLE) {
            message = 'GPS signal is currently unavailable.';
          } else if (error.code === error.TIMEOUT) {
            message = 'Location request timed out. Please try again.';
          }
          reject(new Error(message));
        },
        GPS_OPTIONS
      );
    });
  },

  /**
   * Starts continuous GPS tracking with high accuracy
   */
  watchCurrentLocation: (
    onSuccess: (result: GpsLocationResult) => void,
    onError?: (error: Error) => void
  ): number | null => {
    if (!navigator.geolocation) {
      if (onError) onError(new Error('Geolocation is not supported.'));
      return null;
    }

    return navigator.geolocation.watchPosition(
      (position) => {
        onSuccess({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: Math.round(position.coords.accuracy),
          timestamp: position.timestamp,
        });
      },
      (error) => {
        if (onError) {
          let message = 'Unable to determine your location.';
          if (error.code === error.PERMISSION_DENIED) {
            message = 'Location permission was denied.';
          }
          onError(new Error(message));
        }
      },
      GPS_OPTIONS
    );
  },

  /**
   * Clears an active watchPosition listener
   */
  stopWatchingLocation: (watchId: number | null): void => {
    if (watchId !== null && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId);
    }
  },

  /**
   * Computes distance in meters between two coordinates using Haversine formula
   */
  calculateDistance: (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371e3; // Earth's radius in meters
    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return Math.round(R * c);
  },

  /**
   * Formats coordinates into standard geographical representation (e.g. 16.3067° N, 80.4365° E)
   */
  formatCoordinates: (lat: number, lon: number): string => {
    const latDir = lat >= 0 ? 'N' : 'S';
    const lonDir = lon >= 0 ? 'E' : 'W';
    return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lon).toFixed(4)}° ${lonDir}`;
  }
};
