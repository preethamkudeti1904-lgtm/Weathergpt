export type UserType = 
  | 'General User' 
  | 'Farmer' 
  | 'Researcher' 
  | 'Disaster Management' 
  | 'Government / Official' 
  | 'Aviation' 
  | 'Marine' 
  | 'Student';

export interface User {
  id: number;
  name: string;
  email: string;
  phone_number?: string;
  phone_country_code?: string;
  phone_verified?: boolean;
  phone_verified_at?: string;
  user_type: UserType;
  country?: string;
  state?: string;
  preferred_language: string;
  default_location?: string;
  created_at: string;
}

export interface SmsAlertSettings {
  phone_number?: string;
  masked_phone?: string;
  phone_verified: boolean;
  phone_verified_at?: string;
  sms_alerts_enabled: boolean;
  sms_alert_categories: string[];
  alert_location?: {
    id: number;
    name: string;
    latitude: number;
    longitude: number;
    district?: string;
    state?: string;
    source?: string;
  };
}

export interface SmsDeliveryItem {
  id: number;
  alert_id: string;
  hazard_type: string;
  severity: string;
  phone_number: string;
  message: string;
  status: string;
  provider_message_id?: string;
  sent_at: string;
}


export interface CurrentWeather {
  location_name: string;
  latitude: number;
  longitude: number;
  temperature: number;
  feels_like: number;
  condition: string;
  condition_code: number;
  humidity: number;
  wind_speed: number;
  wind_direction: number;
  wind_direction_cardinal: string;
  wind_gusts?: number;
  pressure: number;
  visibility: number;
  precipitation: number | null;
  uv_index?: number;
  sunrise?: string;
  sunset?: string;
  timezone?: string;
  timezone_abbreviation?: string;
  utc_offset_seconds?: number;
  source: string;
  updated_at: string;
  location?: {
    latitude: number;
    longitude: number;
    name: string;
    timezone?: string;
  };
  current?: {
    temperature: number;
    feels_like: number;
    humidity: number;
    pressure: number;
    wind_speed: number;
    wind_direction: number;
    visibility: number;
    precipitation: number | null;
    condition: string;
  };
  timestamp?: string;
}

export interface HourlyForecast {
  time: string;
  temperature: number;
  condition: string;
  condition_code: number;
  rain_probability: number;
  precipitation: number;
  wind_speed: number;
  wind_direction?: number;
  wind_direction_cardinal?: string;
  wind_gusts?: number;
}

export interface DailyForecast {
  date: string;
  day_name: string;
  condition: string;
  condition_code: number;
  temp_max: number;
  temp_min: number;
  rain_probability: number;
  precipitation: number;
  wind_speed_max: number;
  uv_index_max?: number;
  sunrise?: string;
  sunset?: string;
}

export interface ForecastData {
  location_name: string;
  latitude: number;
  longitude: number;
  current: CurrentWeather;
  hourly: HourlyForecast[];
  daily: DailyForecast[];
  timezone?: string;
  timezone_abbreviation?: string;
  utc_offset_seconds?: number;
  source: string;
  updated_at: string;
}

export interface WeatherAlert {
  id: string;
  title: string;
  category: string;
  severity: 'Information' | 'Watch' | 'Warning' | 'Emergency' | string;
  color_code: 'Green' | 'Yellow' | 'Orange' | 'Red' | string;
  urgency?: string;
  certainty?: string;
  location: string;
  start_time: string;
  end_time: string;
  duration_text?: string;
  description: string;
  source: string;
  recommended_action: string;
  safety_precautions?: string[];
  centroid_lat?: number | null;
  centroid_lon?: number | null;
  radius_km?: number | null;
  distance_km?: number | null;
  is_direct_match?: boolean;
  raw_source?: string;
}

export interface AIRiskAssessment {
  score: number;
  level: 'LOW' | 'MODERATE' | 'HIGH' | 'VERY HIGH' | 'EXTREME' | string;
  confidence: 'High' | 'Moderate' | 'Low' | string;
  expected_window: string;
  reason: string;
  hazard_breakdown: {
    rainfall: number;
    wind: number;
    storm: number;
    temperature: number;
    official_warning_boost: number;
  };
  disclaimer: string;
}

export interface AlertsData {
  location_name: string;
  country?: string;
  state?: string;
  district?: string;
  alerts: WeatherAlert[];
  direct_alerts?: WeatherAlert[];
  regional_alerts?: WeatherAlert[];
  has_active_alerts: boolean;
  ai_risk_assessment?: AIRiskAssessment | null;
  service_status?: 'operational' | 'temporarily_unavailable' | 'no_alerts_found' | string;
  service_message?: string | null;
  source: string;
  updated_at: string;
}


export interface ChatMessageItem {
  id: string | number;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  advisory?: string;
  source_attribution?: string;
  updated_at?: string;
  suggested_questions?: string[];
  timestamp: string;
}

export interface ConversationSummary {
  id: number;
  title: string;
  language: string;
  location_name?: string;
  message_count: number;
  last_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetails {
  id: number;
  title: string;
  language?: string;
  location_name?: string;
  created_at: string;
  updated_at?: string;
  messages: {
    id: number;
    session_id: number;
    role: 'user' | 'assistant';
    content: string;
    intent?: string;
    location_referenced?: string;
    source_attribution?: string;
    timestamp: string;
    created_at?: string;
  }[];
}

export interface CentralLocation {
  latitude: number;
  longitude: number;
  accuracy: number | null;
  name: string;
  city?: string;
  district?: string;
  state?: string;
  country?: string;
  timezone?: string;
  source: 'gps' | 'search' | 'default' | 'ip_approximate' | 'map_click';
  timestamp: string;
}

export interface LocationItem {
  name: string;
  state?: string;
  country: string;
  latitude: number;
  longitude: number;
  display_name: string;
}

export interface ReferenceStationInfo {
  id: string;
  name: string;
  city?: string;
  district?: string;
  state?: string;
  latitude: number;
  longitude: number;
  elevation_m?: number;
  distance_km: number;
}

export interface ClimateSourceInfo {
  organization: string;
  division?: string;
  dataset: string;
  period: string;
  data_type: string;
  attribution: string;
  rain_day_definition: string;
  url?: string;
}

export interface ClimateAnnualSummary {
  mean_temperature_c: number;
  max_temperature_c: number;
  min_temperature_c: number;
  total_precipitation_mm: number;
  rainy_days: number;
  wettest_month: string;
  warmest_month: string;
}

export interface ClimateMonthlyPoint {
  month: string;
  avg_temperature_c: number;
  max_temperature_c: number;
  min_temperature_c: number;
  precipitation_mm: number;
  rain_days: number;
}

export interface LocationMetadata {
  name: string;
  latitude: number;
  longitude: number;
}

export interface ClimateTrendPoint {
  label: string;
  avg_temperature: number;
  max_temperature: number;
  min_temperature: number;
  total_rainfall: number;
  rainfall_days: number;
}

export interface ClimateData {
  location?: LocationMetadata;
  requested_location?: LocationMetadata;
  reference_station?: ReferenceStationInfo;
  source_info?: ClimateSourceInfo;
  annual?: ClimateAnnualSummary;
  monthly?: ClimateMonthlyPoint[];
  location_name: string;
  latitude: number;
  longitude: number;
  period: string;
  historical_period?: string;
  parameter: string;
  data: ClimateTrendPoint[];
  annual_mean_temp: number;
  annual_total_rainfall: number;
  wettest_month?: string;
  warmest_month?: string;
  rain_day_threshold_mm?: number;
  city?: string;
  state?: string;
  country?: string;
  source: string | ClimateSourceInfo;
  updated_at: string;
}

export interface HistoricalYearMonthly {
  month: string;
  avg_temperature: number;
  max_temperature: number;
  min_temperature: number;
  rainfall: number;
  rainy_days: number;
}

export interface HistoricalYearSummary {
  annual_average_temperature: number;
  annual_rainfall: number;
  highest_temperature: number;
  lowest_temperature: number;
  warmest_month: string;
  coldest_month: string;
  wettest_month: string;
  driest_month: string;
  total_rainy_days: number;
}

export interface HistoricalSource {
  name: string;
  station: string;
  station_id?: string;
  distance_km: number;
  dataset?: string;
  data_coverage?: string;
  observation_type?: string;
  rain_day_definition?: string;
  attribution?: string;
}

export interface HistoricalYearResponse {
  location: LocationMetadata;
  year: number;
  source: HistoricalSource;
  monthly: HistoricalYearMonthly[];
  summary: HistoricalYearSummary;
  available_years?: number[];
  climatological_normal?: ClimateData | any;
}

