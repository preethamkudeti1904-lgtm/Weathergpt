import React, { useEffect, useState, useCallback } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import {
  advisoryService,
  AdvisoryResponse,
  AdvisoryItem,
  FieldOperationWindow,
  CROPS_OPTIONS,
  GROWTH_STAGES_OPTIONS
} from '../../services/advisoryService';
import {
  Sprout,
  Droplets,
  Thermometer,
  Wind,
  AlertTriangle,
  CheckCircle2,
  Clock,
  MapPin,
  Calendar,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ShieldCheck,
  Sun,
  Bug,
  Info,
  ExternalLink,
  Sparkles,
  Layers,
  HelpCircle
} from 'lucide-react';

export const FarmerAdvisory: React.FC = () => {
  const { currentLocation, location, latitude, longitude, language, t } = useWeather();

  const [selectedCrop, setSelectedCrop] = useState<string>('rice');
  const [customCropInput, setCustomCropInput] = useState<string>('');
  const [selectedStage, setSelectedStage] = useState<string>('vegetative');
  const [advisoryData, setAdvisoryData] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Expandable sections
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({});
  const [showDebugDrawer, setShowDebugDrawer] = useState<boolean>(false);

  const effectiveCrop = selectedCrop === 'custom' ? (customCropInput.trim() || 'Custom Crop') : selectedCrop;

  const loadAdvisory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await advisoryService.getAdvisory({
        lat: latitude,
        lon: longitude,
        location: currentLocation.name || location,
        crop: effectiveCrop,
        growthStage: selectedStage,
        language: language
      });
      setAdvisoryData(data);
    } catch (err: any) {
      console.error('Failed to load dynamic agricultural advisory:', err);
      setError(err?.message || 'Advisory temporarily unavailable because current weather data could not be retrieved.');
    } finally {
      setLoading(false);
    }
  }, [latitude, longitude, currentLocation.name, location, effectiveCrop, selectedStage, language]);

  useEffect(() => {
    loadAdvisory();
  }, [loadAdvisory]);

  const toggleExpand = (id: string) => {
    setExpandedCards((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-950/80 dark:text-red-300 border-red-300 dark:border-red-800';
      case 'high':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 border-amber-300 dark:border-amber-800';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/80 dark:text-yellow-300 border-yellow-300 dark:border-yellow-800';
      case 'low':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-950/80 dark:text-blue-300 border-blue-300 dark:border-blue-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    const c = category?.toLowerCase();
    if (c.includes('irrigation')) return <Droplets className="w-4 h-4 text-cyan-500" />;
    if (c.includes('spray')) return <Wind className="w-4 h-4 text-indigo-500" />;
    if (c.includes('pest') || c.includes('disease')) return <Bug className="w-4 h-4 text-amber-500" />;
    if (c.includes('drainage') || c.includes('rain')) return <Droplets className="w-4 h-4 text-blue-600" />;
    if (c.includes('temperature') || c.includes('heat') || c.includes('cold')) return <Thermometer className="w-4 h-4 text-red-500" />;
    if (c.includes('wind')) return <Wind className="w-4 h-4 text-teal-500" />;
    if (c.includes('harvest')) return <Sun className="w-4 h-4 text-amber-600" />;
    if (c.includes('fertilizer')) return <Sprout className="w-4 h-4 text-emerald-500" />;
    return <Sprout className="w-4 h-4 text-primary-500" />;
  };

  const obs = advisoryData?.meteorological_observations;

  return (
    <div className="space-y-6">
      {/* Header Banner with Location & Selectors */}
      <div className="bg-gradient-to-r from-emerald-800 via-emerald-700 to-teal-800 text-white rounded-2xl p-5 sm:p-6 shadow-md border border-emerald-600/40">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="flex items-start gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur border border-white/20 flex items-center justify-center text-3xl flex-shrink-0">
              🌾
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-lg sm:text-xl font-bold tracking-tight">
                  {t('nav_crop_advisory') || 'Crop Weather Advisory (Agro-Met)'}
                </h1>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-900/60 border border-emerald-400/40 text-emerald-200">
                  Location Grounded
                </span>
              </div>
              <p className="text-xs text-emerald-100 mt-1 max-w-2xl">
                Location-specific, weather-driven agronomic guidance calculated from real meteorological observations and 7-day forecast projections for{' '}
                <span className="font-semibold text-white underline decoration-emerald-300/60 underline-offset-2">
                  {advisoryData?.location?.name || currentLocation.name || location}
                </span>
              </p>
              <div className="flex items-center gap-3 text-[11px] text-emerald-200/90 mt-2 font-mono">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-emerald-300" />
                  {latitude.toFixed(4)}° N, {longitude.toFixed(4)}° E
                </span>
                <span>•</span>
                <span>{advisoryData?.location?.state || 'State Agromet Zone'}</span>
                <span>•</span>
                <span className="capitalize">{currentLocation.source === 'gps' ? 'Live GPS' : 'Station Search'}</span>
              </div>
            </div>
          </div>

          {/* Action Controls: Crop & Stage Selectors + Refresh */}
          <div className="flex flex-wrap items-center gap-2.5 bg-black/20 backdrop-blur p-3 rounded-xl border border-white/10 self-start lg:self-center">
            {/* Crop Selector */}
            <div>
              <label className="block text-[10px] uppercase font-bold text-emerald-200 mb-1">
                Crop
              </label>
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="bg-emerald-900/90 border border-emerald-500/60 text-white text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-300"
              >
                {CROPS_OPTIONS.map((c) => (
                  <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Custom Crop Input if Custom is Selected */}
            {selectedCrop === 'custom' && (
              <div>
                <label className="block text-[10px] uppercase font-bold text-emerald-200 mb-1">
                  Custom Crop Name
                </label>
                <input
                  type="text"
                  value={customCropInput}
                  onChange={(e) => setCustomCropInput(e.target.value)}
                  placeholder="e.g. Mustard, Banana..."
                  className="bg-emerald-900/90 border border-emerald-500/60 text-white text-xs rounded-lg px-2.5 py-1.5 focus:outline-none placeholder-emerald-300/50 w-32"
                />
              </div>
            )}

            {/* Growth Stage Selector */}
            <div>
              <label className="block text-[10px] uppercase font-bold text-emerald-200 mb-1">
                Growth Stage
              </label>
              <select
                value={selectedStage}
                onChange={(e) => setSelectedStage(e.target.value)}
                className="bg-emerald-900/90 border border-emerald-500/60 text-white text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-300"
              >
                {GROWTH_STAGES_OPTIONS.map((s) => (
                  <option key={s.id} value={s.id} className="bg-slate-900 text-white">
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Refresh Button */}
            <div className="self-end">
              <button
                onClick={loadAdvisory}
                disabled={loading}
                className="p-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1 transition shadow-sm disabled:opacity-50"
                title="Refresh advisory with latest weather data"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Banner if API Fails (Section 31: Honest handling) */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-xs font-bold text-red-800 dark:text-red-200">
              Advisory Temporarily Unavailable
            </h3>
            <p className="text-xs text-red-600 dark:text-red-300 mt-0.5">
              {error}
            </p>
          </div>
          <button
            onClick={loadAdvisory}
            className="px-3 py-1 bg-red-600 text-white text-xs font-semibold rounded-lg hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      )}

      {/* Section 1: Dynamic Weather Observations Bar (Section 34) */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
        <div className="flex items-center justify-between mb-3.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Verified Meteorological Observations
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-200 dark:border-emerald-800">
              {advisoryData?.crop_display_name || effectiveCrop} • {advisoryData?.growth_stage_display_name || selectedStage}
            </span>
          </div>
          <span className="text-[11px] text-slate-400">
            Source: {obs?.source || 'Open-Meteo & IMD Ground Observations'}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          {/* 7-Day Cumulative Rainfall (Calculated sum from real daily forecast) */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-blue-500" /> 7-Day Rainfall
            </span>
            <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {obs?.seven_day_cumulative_rainfall || '0.0 mm'}
            </div>
            <span className="text-[10px] text-slate-400">
              Next 24h: {obs?.next_24h_expected_rainfall || '0 mm'} ({obs?.next_24h_rain_probability || '0%'} prob)
            </span>
          </div>

          {/* Daytime Temperature */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5 text-amber-500" /> Daytime Temp
            </span>
            <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {obs?.current_temperature || 'N/A'}
            </div>
            <span className="text-[10px] text-slate-400">
              High: {obs?.daytime_high || 'N/A'} • Low: {obs?.nighttime_low || 'N/A'}
            </span>
          </div>

          {/* Relative Humidity */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-teal-500" /> Relative Humidity
            </span>
            <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {obs?.relative_humidity || 'N/A'}
            </div>
            <span className="text-[10px] text-slate-400">
              Soil: {obs?.soil_moisture_status?.split('(')[0]?.trim() || 'Calculated water balance'}
            </span>
          </div>

          {/* Wind Speed & Direction */}
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
            <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Wind className="w-3.5 h-3.5 text-indigo-500" /> Wind Speed
            </span>
            <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
              {obs?.wind_speed || 'N/A'}
            </div>
            <span className="text-[10px] text-slate-400">
              Direction: {obs?.wind_direction || 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Section 2: Best Field Work Window Card (Section 19) */}
      {advisoryData?.field_operation_windows && advisoryData.field_operation_windows.length > 0 && (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-blue-200 dark:border-blue-900/60 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <h2 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Best Field Operation Windows (Next 3 Days)
              </h2>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-semibold border border-blue-200 dark:border-blue-800">
              Hourly Forecast Derived
            </span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mb-3.5">
            Computed from hourly precipitation probability, wind drift thresholds, and temperature limits for field work.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {advisoryData.field_operation_windows.map((w: FieldOperationWindow, idx: number) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-xs text-slate-800 dark:text-slate-200">
                      {w.day} ({w.date})
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        w.status === 'Favorable'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : w.status === 'Marginal'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300'
                      }`}
                    >
                      {w.status} ({w.suitability_score}/100)
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-primary-600 dark:text-primary-400 mb-1">
                    {w.time_slot}
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 space-y-0.5 font-mono">
                    <div>Rain Risk: {w.rain_risk_percent}%</div>
                    <div>Wind Speed: {w.wind_speed_kmh} km/h • Temp: {w.temperature_c}°C</div>
                  </div>
                </div>

                <div className="mt-2.5 pt-2 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-300">
                  <span className="font-semibold block text-[10px] uppercase text-slate-400">Suitable Operations:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {w.recommended_operations.map((op, opIdx) => (
                      <span key={opIdx} className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 text-[10px] font-medium border border-slate-200 dark:border-slate-700">
                        {op}
                      </span>
                    ))}
                  </div>
                  {w.caution_notes && (
                    <div className="text-[10px] text-slate-400 mt-1 italic">
                      {w.caution_notes}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section 3: Weather-Driven Crop Advisories (Categorized Priority Cards) */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-500" />
              Weather-Driven Agricultural Advisories
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Scientific rules triggered for {advisoryData?.crop_display_name || effectiveCrop} ({advisoryData?.growth_stage_display_name || selectedStage}) based on live forecast
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {advisoryData?.advisories?.length || 0} Rules Active
          </span>
        </div>

        {loading ? (
          <div className="p-10 text-center flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 text-emerald-500 animate-spin" />
            <p className="text-xs text-slate-500">
              Evaluating crop phonological thresholds against forecast models...
            </p>
          </div>
        ) : advisoryData?.advisories && advisoryData.advisories.length > 0 ? (
          <div className="grid grid-cols-1 gap-3.5">
            {advisoryData.advisories.map((adv: AdvisoryItem) => {
              const isExpanded = Boolean(expandedCards[adv.id]);
              return (
                <div
                  key={adv.id}
                  className="rounded-xl border border-slate-200 dark:border-slate-800 p-4 sm:p-5 bg-slate-50/60 dark:bg-slate-850/60 hover:bg-white dark:hover:bg-slate-850 transition shadow-sm"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm flex-shrink-0 mt-0.5">
                        {getCategoryIcon(adv.category)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                            {adv.category}
                          </span>
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${getPriorityBadgeClass(adv.priority)}`}>
                            {adv.priority} Priority
                          </span>
                          <span className="text-[11px] text-slate-400">
                            Window: {adv.time_window}
                          </span>
                        </div>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                          {adv.title}
                        </h3>
                        <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                          <span className="font-semibold text-slate-800 dark:text-slate-200">Recommended Action: </span>
                          {adv.recommendation}
                        </p>
                      </div>
                    </div>

                    <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2 flex-shrink-0">
                      <span className="text-[10px] font-semibold text-slate-400">
                        Confidence: <span className="text-slate-700 dark:text-slate-200">{adv.confidence}</span>
                      </span>
                      <button
                        onClick={() => toggleExpand(adv.id)}
                        className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1"
                      >
                        <span>{isExpanded ? 'Hide Evidence' : 'Why this advice?'}</span>
                        {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Expandable Section 24: "Why am I getting this advice?" */}
                  {isExpanded && (
                    <div className="mt-3.5 pt-3 border-t border-slate-200 dark:border-slate-800 space-y-2.5 text-xs bg-white dark:bg-slate-900 p-3.5 rounded-lg border">
                      <div>
                        <span className="font-bold text-slate-700 dark:text-slate-300 uppercase text-[10px] tracking-wider block">
                          Agronomic Meteorological Evidence:
                        </span>
                        <p className="text-slate-600 dark:text-slate-300 text-xs mt-0.5">
                          {adv.reason}
                        </p>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono text-[11px]">
                        <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
                          <span className="text-[10px] text-slate-400 block font-sans">Current Temp:</span>
                          <span className="font-bold">{adv.weather_evidence?.current_temp}°C</span>
                        </div>
                        <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
                          <span className="text-[10px] text-slate-400 block font-sans">24h Rain Prob:</span>
                          <span className="font-bold">{adv.weather_evidence?.precipitation_probability_24h}%</span>
                        </div>
                        <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
                          <span className="text-[10px] text-slate-400 block font-sans">Wind Speed:</span>
                          <span className="font-bold">{adv.weather_evidence?.wind_speed} km/h</span>
                        </div>
                        <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
                          <span className="text-[10px] text-slate-400 block font-sans">Relative Humidity:</span>
                          <span className="font-bold">{adv.weather_evidence?.relative_humidity}%</span>
                        </div>
                      </div>

                      <div className="text-[11px] text-slate-400 pt-1 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 dark:border-slate-800">
                        <span>Source: {adv.source}</span>
                        <span>Confidence: {adv.confidence_reason}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-slate-400">
            No specific agricultural threshold alerts triggered for current weather parameters.
          </div>
        )}
      </div>

      {/* Section 4: Official vs AI Advisory Separation (Section 32) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Left: Official IMD Bulletin */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-amber-200 dark:border-amber-900/60 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <h3 className="text-xs font-bold text-amber-800 dark:text-amber-300 uppercase tracking-wider">
                Official Agricultural Advisory (IMD / GKMS)
              </h3>
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white mt-1">
              {advisoryData?.official_bulletin?.bulletin_title || 'District Agro-Met Advisory Bulletin'}
            </h4>
            <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
              {advisoryData?.official_bulletin?.summary}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
            <span>Issued by: {advisoryData?.official_bulletin?.issuing_authority}</span>
            {advisoryData?.official_bulletin?.source_url && (
              <a
                href={advisoryData.official_bulletin.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1 font-semibold"
              >
                <span>IMD Portal</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>

        {/* Right: WeatherGPT AI Weather-Based Analysis Notice */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-emerald-200 dark:border-emerald-900/60 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider">
                WeatherGPT Agro-Met Weather Intelligence
              </h3>
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white mt-1">
              Deterministic Meteorological Threshold Engine
            </h4>
            <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
              {advisoryData?.system_disclaimer ||
                'AI-generated advisory based on live meteorological observations and phonological crop thresholds. Guidance only. Cross-verify with district KVK / State Agriculture Department.'}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
            <span>Rules Sourced from ICAR & State Agricultural Universities</span>
            <button
              onClick={() => setShowDebugDrawer(!showDebugDrawer)}
              className="text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1 font-semibold"
            >
              <Bug className="w-3 h-3" />
              <span>{showDebugDrawer ? 'Hide Diagnostics' : 'Dev Diagnostics'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Section 5: Data Freshness Bar (Section 25 & 26: Local Timezone) */}
      <div className="bg-slate-100 dark:bg-slate-800/80 rounded-xl p-3.5 border border-slate-200 dark:border-slate-700 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-600 dark:text-slate-400">
        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-primary-500" />
          <span>
            Weather Observed: <strong className="text-slate-800 dark:text-slate-200">{obs?.observation_time || 'Recent'}</strong>
          </span>
        </div>
        <div>
          Forecast Updated: <strong className="text-slate-800 dark:text-slate-200">{obs?.forecast_time || 'Recent'}</strong>
        </div>
        <div>
          Advisory Generated: <strong className="text-slate-800 dark:text-slate-200">{advisoryData?.data_freshness?.advisory_generated || 'Live'}</strong>
        </div>
        <div className="font-mono text-[11px]">
          Timezone: {advisoryData?.data_freshness?.location_timezone || 'Asia/Kolkata'}
        </div>
      </div>

      {/* Section 6: Developer Diagnostic Drawer (Section 37) */}
      {showDebugDrawer && (
        <div className="p-4 rounded-xl bg-slate-900 text-slate-200 text-xs font-mono space-y-2 border border-slate-700">
          <div className="flex items-center justify-between pb-1 border-b border-slate-800">
            <span className="font-bold text-amber-400">Agromet Engine Diagnostic Inspector</span>
            <span className="text-[10px] text-slate-400">DEV MODE ONLY</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            <div>Location: {advisoryData?.location?.name} ({latitude.toFixed(4)}, {longitude.toFixed(4)})</div>
            <div>Location Source: {currentLocation.source}</div>
            <div>Active Crop: {selectedCrop} ({advisoryData?.crop_display_name})</div>
            <div>Active Stage: {selectedStage} ({advisoryData?.growth_stage_display_name})</div>
            <div>Current Temp: {obs?.current_temperature} • RH: {obs?.relative_humidity}</div>
            <div>7-Day Forecast Rain Sum: {obs?.seven_day_cumulative_rainfall}</div>
            <div>Active Rules Triggered: {advisoryData?.triggered_rules_count}</div>
            <div>Soil Moisture Status: {obs?.soil_moisture_status}</div>
          </div>
        </div>
      )}
    </div>
  );
};
