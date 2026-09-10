import {
  CurrentWeather,
  ForecastData,
  AlertsData,
  ClimateData,
  LocationItem,
  User,
  UserType,
  ConversationSummary,
  ChatSessionDetails
} from '../types';

export const API_BASE = '/api';

export const api = {
  // Weather
  getCurrentWeather: async (location: string, lat?: number, lon?: number): Promise<CurrentWeather> => {
    const params = new URLSearchParams({ location });
    if (lat !== undefined && lon !== undefined) {
      params.append('lat', lat.toString());
      params.append('lon', lon.toString());
    }
    const res = await fetch(`${API_BASE}/weather/current?${params.toString()}`);
    if (!res.ok) throw new Error('Unable to retrieve weather data right now.');
    return res.json();
  },

  getForecast: async (location: string, days: number = 7, lat?: number, lon?: number): Promise<ForecastData> => {
    const params = new URLSearchParams({ location, days: days.toString() });
    if (lat !== undefined && lon !== undefined) {
      params.append('lat', lat.toString());
      params.append('lon', lon.toString());
    }
    const res = await fetch(`${API_BASE}/weather/forecast?${params.toString()}`);
    if (!res.ok) throw new Error('Unable to retrieve forecast right now.');
    return res.json();
  },

  getAlerts: async (location: string, lat?: number, lon?: number): Promise<AlertsData> => {
    const params = new URLSearchParams({ location });
    if (lat !== undefined && lon !== undefined) {
      params.append('lat', lat.toString());
      params.append('lon', lon.toString());
    }
    const res = await fetch(`${API_BASE}/weather/alerts?${params.toString()}`);
    if (!res.ok) throw new Error('Unable to retrieve weather alerts right now.');
    return res.json();
  },

  // Chat & Persistent Conversations
  sendChatMessage: async (payload: {
    message: string;
    location?: Record<string, any>;
    location_name?: string;
    latitude?: number;
    longitude?: number;
    timezone?: string;
    local_time?: string;
    local_date?: string;
    language?: string;
    user_type?: string;
    session_id?: number;
    conversation_id?: string | number;
  }) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('WeatherGPT could not respond. Please try again.');
    return res.json();
  },

  getConversations: async (search?: string): Promise<ConversationSummary[]> => {
    const token = localStorage.getItem('weathergpt_token');
    const params = search && search.trim() ? `?search=${encodeURIComponent(search.trim())}` : '';
    const res = await fetch(`${API_BASE}/chat/conversations${params}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) return [];
    return res.json();
  },

  getConversationDetails: async (conversationId: number): Promise<ChatSessionDetails> => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) throw new Error('Failed to load conversation details');
    return res.json();
  },

  createConversation: async (data: {
    title?: string;
    language?: string;
    location_name?: string;
    latitude?: number;
    longitude?: number;
  }): Promise<ChatSessionDetails> => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/chat/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create new conversation');
    return res.json();
  },

  updateConversationTitle: async (conversationId: number, title: string): Promise<ChatSessionDetails> => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ title })
    });
    if (!res.ok) throw new Error('Failed to update conversation title');
    return res.json();
  },

  deleteConversation: async (conversationId: number): Promise<{ message: string; id: number }> => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
      method: 'DELETE',
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) throw new Error('Failed to delete conversation');
    return res.json();
  },

  getChatSessions: async () => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/chat/sessions`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) return [];
    return res.json();
  },

  // Locations
  searchLocations: async (query: string): Promise<LocationItem[]> => {
    if (!query.trim()) return [];
    const res = await fetch(`${API_BASE}/locations/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) return [];
    return res.json();
  },

  reverseGeocode: async (lat: number, lon: number): Promise<{
    name: string;
    city?: string;
    district?: string;
    state?: string;
    country: string;
    display_name: string;
    full_address: string;
    latitude: number;
    longitude: number;
  }> => {
    try {
      const res = await fetch(`${API_BASE}/locations/reverse?lat=${lat}&lon=${lon}`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.name && data.name !== 'Location') {
          return data;
        }
      }
    } catch (e) {
      console.warn('Backend reverse geocode error, attempting client fallback:', e);
    }

    // Direct client fallback to BigDataCloud reverse geocoding API (free, reliable, global)
    try {
      const clientRes = await fetch(
        `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`
      );
      if (clientRes.ok) {
        const bdc = await clientRes.json();
        const locality = bdc.locality || bdc.city || bdc.principalSubdivision || `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`;
        const state = bdc.principalSubdivision || '';
        const country = bdc.countryName || 'India';
        const display = state ? `${locality}, ${state}` : locality;
        return {
          name: locality,
          city: bdc.city || locality,
          district: bdc.localityInfo?.administrative?.[2]?.name || '',
          state: state,
          country: country,
          display_name: display,
          full_address: display,
          latitude: lat,
          longitude: lon,
        };
      }
    } catch (err) {
      console.warn('Client reverse geocode error:', err);
    }

    return {
      name: `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`,
      display_name: `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`,
      full_address: `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`,
      country: 'India',
      latitude: lat,
      longitude: lon,
    };
  },

  getSavedLocations: async (): Promise<any[]> => {
    const res = await fetch(`${API_BASE}/locations/saved`);
    if (!res.ok) return [];
    return res.json();
  },

  saveLocation: async (data: { location_name: string; state?: string; country?: string; latitude: number; longitude: number }) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/locations/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to save location');
    return res.json();
  },

  // Climate
  getClimateHistory: async (location: string, lat?: number, lon?: number): Promise<ClimateData> => {
    const params = new URLSearchParams({ location });
    if (lat !== undefined && lon !== undefined) {
      params.append('lat', lat.toString());
      params.append('lon', lon.toString());
    }
    const res = await fetch(`${API_BASE}/climate/history?${params.toString()}`);
    if (!res.ok) throw new Error('Unable to retrieve climate history.');
    return res.json();
  },

  // Role Advisories
  getCropAdvisory: async (
    location: string,
    crop?: string,
    lat?: number,
    lon?: number,
    growthStage?: string,
    language?: string
  ) => {
    const params = new URLSearchParams({ location });
    if (crop) params.append('crop', crop);
    if (lat !== undefined && lat !== null) params.append('lat', lat.toString());
    if (lon !== undefined && lon !== null) params.append('lon', lon.toString());
    if (growthStage) params.append('growth_stage', growthStage);
    if (language) params.append('language', language);
    const res = await fetch(`${API_BASE}/advisory?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to load crop advisory');
    return res.json();
  },

  getDisasterDashboard: async (location: string) => {
    const res = await fetch(`${API_BASE}/advisory/disaster?location=${encodeURIComponent(location)}`);
    if (!res.ok) throw new Error('Failed to load disaster dashboard');
    return res.json();
  },

  getAviationWeather: async (location: string) => {
    const res = await fetch(`${API_BASE}/advisory/aviation?location=${encodeURIComponent(location)}`);
    if (!res.ok) throw new Error('Failed to load aviation weather');
    return res.json();
  },

  getMarineWeather: async (location: string) => {
    const res = await fetch(`${API_BASE}/advisory/marine?location=${encodeURIComponent(location)}`);
    if (!res.ok) throw new Error('Failed to load marine weather');
    return res.json();
  },

  // Auth
  register: async (userData: any) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    if (!res.ok) {
      let errMsg = 'Unable to create your account right now. Please try again.';
      try {
        const err = await res.json();
        if (typeof err.detail === 'string') {
          errMsg = err.detail;
        } else if (Array.isArray(err.detail) && err.detail[0]?.msg) {
          errMsg = err.detail[0].msg.replace(/^Value error,\s*/i, '');
        }
      } catch {}

      const lower = errMsg.toLowerCase();
      if (lower.includes('72 bytes') || lower.includes('longer than 72') || lower.includes('too long')) {
        errMsg = 'Password is too long. Please choose a shorter password.';
      }
      throw new Error(errMsg);
    }
    return res.json();
  },

  login: async (credentials: { email: string; password: string }) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  getMe: async (token: string): Promise<User> => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to load profile');
    return res.json();
  },

  updateUserType: async (user_type: UserType, token: string): Promise<User> => {
    const res = await fetch(`${API_BASE}/auth/user-type`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ user_type }),
    });
    if (!res.ok) throw new Error('Failed to update user role');
    return res.json();
  },

  updatePreferences: async (
    prefs: { language?: string; theme?: string; temperature_unit?: string; wind_unit?: string },
    token: string
  ) => {
    const res = await fetch(`${API_BASE}/auth/preferences`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(prefs),
    });
    if (!res.ok) throw new Error('Failed to update preferences');
    return res.json();
  },

  // Personalized Location Disaster Alerts
  saveAlertLocation: async (locationData: {
    latitude: number;
    longitude: number;
    location_name: string;
    locality?: string;
    village?: string;
    mandal?: string;
    district?: string;
    state?: string;
    country?: string;
    timezone?: string;
    accuracy?: number | null;
    source?: string;
    label?: string;
    is_primary?: boolean;
    is_active?: boolean;
  }) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/alerts/location`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(locationData)
    });
    if (!res.ok) throw new Error('Failed to save alert location');
    return res.json();
  },

  getMyAlertLocations: async () => {
    const token = localStorage.getItem('weathergpt_token');
    if (!token) return { locations: [], total: 0, push_enabled: false, monitoring_active: false };
    const res = await fetch(`${API_BASE}/alerts/my-location`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return { locations: [], total: 0, push_enabled: false, monitoring_active: false };
    return res.json();
  },

  updateAlertLocation: async (locationId: number, data: { label?: string; is_active?: boolean; is_primary?: boolean }) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/alerts/location/${locationId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update alert location');
    return res.json();
  },

  deleteAlertLocation: async (locationId: number) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/alerts/location/${locationId}`, {
      method: 'DELETE',
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) throw new Error('Failed to delete alert location');
    return res.json();
  },

  getActivePersonalizedAlerts: async (params?: { lat?: number; lon?: number; district?: string; state?: string }) => {
    const token = localStorage.getItem('weathergpt_token');
    const query = new URLSearchParams();
    if (params?.lat !== undefined) query.append('lat', params.lat.toString());
    if (params?.lon !== undefined) query.append('lon', params.lon.toString());
    if (params?.district) query.append('district', params.district);
    if (params?.state) query.append('state', params.state);

    const res = await fetch(`${API_BASE}/alerts/active?${query.toString()}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) throw new Error('Failed to load active personalized alerts');
    return res.json();
  },

  getAlertHistory: async (limit: number = 20) => {
    const token = localStorage.getItem('weathergpt_token');
    if (!token) return { deliveries: [], total: 0 };
    const res = await fetch(`${API_BASE}/alerts/history?limit=${limit}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return { deliveries: [], total: 0 };
    return res.json();
  },

  getAlertMonitorStatus: async () => {
    const res = await fetch(`${API_BASE}/alerts/status`);
    if (!res.ok) return null;
    return res.json();
  },

  triggerTestAlert: async (payload: {
    hazard_type: string;
    severity: string;
    title?: string;
    description?: string;
    instructions?: string;
    is_inside_user_area: boolean;
    is_update?: boolean;
  }) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/alerts/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to trigger simulated alert');
    return res.json();
  },

  // Web Push Subscriptions
  getVapidPublicKey: async () => {
    const res = await fetch(`${API_BASE}/notifications/vapid-public-key`);
    if (!res.ok) throw new Error('Failed to get VAPID key');
    return res.json();
  },

  savePushSubscription: async (data: { endpoint: string; p256dh: string; auth: string; user_agent?: string }) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/notifications/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to register push subscription');
    return res.json();
  },

  deletePushSubscription: async (endpoint: string) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/notifications/subscribe?endpoint=${encodeURIComponent(endpoint)}`, {
      method: 'DELETE',
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) throw new Error('Failed to unregister push subscription');
    return res.json();
  },

  // Phone OTP & Disaster SMS Alert Methods
  sendPhoneOtp: async (phoneNumber?: string, countryCode: string = '+91') => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/auth/send-phone-otp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ phone_number: phoneNumber, phone_country_code: countryCode })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to send OTP. Please check your phone number.');
    }
    return res.json();
  },

  verifyPhoneOtp: async (phoneNumber: string, otp: string) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/auth/verify-phone-otp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ phone_number: phoneNumber, otp })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid OTP code. Please try again.');
    }
    return res.json();
  },

  getSmsAlertSettings: async () => {
    const token = localStorage.getItem('weathergpt_token');
    if (!token) return null;
    const res = await fetch(`${API_BASE}/settings/sms-alerts`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return null;
    return res.json();
  },

  updateSmsAlertSettings: async (sms_alerts_enabled: boolean, categories?: string[]) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/settings/sms-alerts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ sms_alerts_enabled, sms_alert_categories: categories })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update SMS disaster alert preferences.');
    }
    return res.json();
  },

  getSmsAlertHistory: async (limit: number = 25) => {
    const token = localStorage.getItem('weathergpt_token');
    if (!token) return { deliveries: [], total: 0 };
    const res = await fetch(`${API_BASE}/alerts/sms-history?limit=${limit}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return { deliveries: [], total: 0 };
    return res.json();
  },

  sendTestSms: async (hazard_type: string = 'Heavy Rain', severity: string = 'Warning', is_inside_user_area: boolean = true) => {
    const token = localStorage.getItem('weathergpt_token');
    const res = await fetch(`${API_BASE}/notifications/test-sms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ hazard_type, severity, is_inside_user_area })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Test SMS dispatch failed.');
    }
    return res.json();
  }
};

