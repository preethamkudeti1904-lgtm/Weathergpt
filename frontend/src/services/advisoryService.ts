import { API_BASE } from './api';

export interface WeatherEvidence {
  current_temp?: number;
  max_temp?: number;
  min_temp?: number;
  relative_humidity?: number;
  wind_speed?: number;
  wind_gust?: number;
  precipitation_next_24h?: number;
  precipitation_probability_24h?: number;
  precipitation_7d_total?: number;
  soil_moisture_estimate?: string;
  evapotranspiration_et0?: number;
  cloud_cover?: number;
  uv_index?: number;
}

export interface AdvisoryItem {
  id: string;
  category: string;
  title: string;
  priority: 'Critical' | 'High' | 'Moderate' | 'Low' | 'Information' | string;
  reason: string;
  weather_evidence: WeatherEvidence;
  recommendation: string;
  time_window: string;
  confidence: 'High' | 'Medium' | 'Low' | string;
  confidence_reason: string;
  source: string;
  generated_at: string;
}

export interface FieldOperationWindow {
  day: string;
  date: string;
  time_slot: string;
  status: 'Favorable' | 'Marginal' | 'Unfavorable' | string;
  suitability_score: number;
  rain_risk_percent: number;
  wind_speed_kmh: number;
  temperature_c: number;
  recommended_operations: string[];
  caution_notes?: string | null;
}

export interface MeteorologicalObservations {
  current_temperature: string;
  daytime_high: string;
  nighttime_low: string;
  relative_humidity: string;
  wind_speed: string;
  wind_direction: string;
  next_24h_expected_rainfall: string;
  next_24h_rain_probability: string;
  seven_day_cumulative_rainfall: string;
  soil_moisture_status: string;
  uv_index: string;
  source: string;
  observation_time: string;
  forecast_time: string;
}

export interface OfficialBulletin {
  issuing_authority: string;
  bulletin_title: string;
  target_area: string;
  validity_period: string;
  summary: string;
  source_url?: string;
  disclaimer: string;
}

export interface ClimateContext {
  historical_period: string;
  monthly_mean_temp?: number;
  monthly_normal_rainfall?: number;
  wettest_month?: string;
  warmest_month?: string;
  source: string;
}

export interface AdvisoryResponse {
  location: {
    name: string;
    district?: string;
    state?: string;
    country: string;
    latitude: number;
    longitude: number;
    timezone: string;
    source: string;
  };
  crop: string;
  crop_display_name: string;
  growth_stage: string;
  growth_stage_display_name: string;
  language: string;
  meteorological_observations: MeteorologicalObservations;
  climate_context?: ClimateContext | null;
  advisories: AdvisoryItem[];
  field_operation_windows: FieldOperationWindow[];
  official_bulletin: OfficialBulletin;
  data_freshness: {
    weather_observed: string;
    forecast_computed: string;
    advisory_generated: string;
    location_timezone: string;
  };
  triggered_rules_count: number;
  system_disclaimer: string;
}

export interface CropOption {
  id: string;
  name: string;
  scientific_name: string;
  category: string;
}

export interface GrowthStageOption {
  id: string;
  name: string;
  description: string;
}

export const CROPS_OPTIONS: CropOption[] = [
  { id: 'rice', name: 'Rice / Paddy', scientific_name: 'Oryza sativa', category: 'Cereal' },
  { id: 'cotton', name: 'Cotton', scientific_name: 'Gossypium hirsutum', category: 'Fiber' },
  { id: 'chilli', name: 'Chilli', scientific_name: 'Capsicum annuum', category: 'Spice / Cash' },
  { id: 'maize', name: 'Maize', scientific_name: 'Zea mays', category: 'Cereal' },
  { id: 'groundnut', name: 'Groundnut', scientific_name: 'Arachis hypogaea', category: 'Oilseed' },
  { id: 'sugarcane', name: 'Sugarcane', scientific_name: 'Saccharum officinarum', category: 'Sugar / Cash' },
  { id: 'turmeric', name: 'Turmeric', scientific_name: 'Curcuma longa', category: 'Spice / Cash' },
  { id: 'pulses', name: 'Pulses', scientific_name: 'Legumes (Vigna / Cajanus)', category: 'Pulse' },
  { id: 'vegetables', name: 'Vegetables', scientific_name: 'Horticultural Crops', category: 'Horticulture' },
  { id: 'tomato', name: 'Tomato', scientific_name: 'Solanum lycopersicum', category: 'Vegetable' },
  { id: 'onion', name: 'Onion', scientific_name: 'Allium cepa', category: 'Vegetable' },
  { id: 'custom', name: 'Custom Crop', scientific_name: 'User-specified crop', category: 'Custom' }
];

export const GROWTH_STAGES_OPTIONS: GrowthStageOption[] = [
  { id: 'land_preparation', name: 'Land Preparation', description: 'Tillage, plowing, and seedbed preparation' },
  { id: 'sowing', name: 'Sowing', description: 'Seed drilling, broadcasting, or direct seeding' },
  { id: 'germination', name: 'Germination', description: 'Sprouting and radicle emergence' },
  { id: 'seedling', name: 'Seedling / Nursery', description: 'Nursery bed or young seedling establishment' },
  { id: 'vegetative', name: 'Vegetative / Tillering', description: 'Active foliage growth, branching, or tillering' },
  { id: 'flowering', name: 'Flowering / Anthesis', description: 'Bloom, panicle emergence, and pollination' },
  { id: 'fruiting', name: 'Fruiting / Boll Development', description: 'Fruit set, pod formation, or boll swelling' },
  { id: 'grain_filling', name: 'Grain Filling / Milking', description: 'Milking to dough stage grain development' },
  { id: 'maturity', name: 'Maturity / Ripening', description: 'Physiological maturity and moisture loss' },
  { id: 'harvest', name: 'Harvest', description: 'Reaping, threshing, lifting, or picking' },
  { id: 'post_harvest', name: 'Post-Harvest / Drying', description: 'Field curing, sun-drying, and storage preparation' }
];

export const advisoryService = {
  getAdvisory: async (params: {
    lat?: number;
    lon?: number;
    location?: string;
    crop?: string;
    growthStage?: string;
    language?: string;
  }): Promise<AdvisoryResponse> => {
    const q = new URLSearchParams();
    if (params.lat !== undefined && params.lat !== null) q.append('lat', params.lat.toString());
    if (params.lon !== undefined && params.lon !== null) q.append('lon', params.lon.toString());
    if (params.location) q.append('location', params.location);
    if (params.crop) q.append('crop', params.crop);
    if (params.growthStage) q.append('growth_stage', params.growthStage);
    if (params.language) q.append('language', params.language);

    const res = await fetch(`${API_BASE}/advisory?${q.toString()}`);
    if (!res.ok) {
      const errText = await res.text().catch(() => 'Advisory request failed');
      throw new Error(errText || 'Advisory temporarily unavailable because current weather data could not be retrieved.');
    }
    return res.json();
  }
};
