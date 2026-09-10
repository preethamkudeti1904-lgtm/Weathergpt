import React, { useEffect, useState, useCallback } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { api } from '../../services/api';
import { ClimateData } from '../../types';
import {
  BarChart3,
  Download,
  Calendar,
  Layers,
  Thermometer,
  Droplets,
  Table,
  FileSpreadsheet,
  RefreshCw,
  AlertTriangle,
  MapPin,
  Clock,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';

export const ResearcherAnalytics: React.FC = () => {
  const { location, latitude, longitude } = useWeather();
  const [climate, setClimate] = useState<ClimateData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadClimate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getClimateHistory(location, latitude, longitude);
      if (!res || !res.data || !Array.isArray(res.data) || res.data.length !== 12) {
        throw new Error('Incomplete or unverified climate data received.');
      }
      setClimate(res);
    } catch (err: any) {
      console.error('Climate load failed:', err);
      setClimate(null);
      setError('Climate data temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  }, [location, latitude, longitude]);

  useEffect(() => {
    // Reset climate when coordinates or location changes so previous data never persists
    setClimate(null);
    loadClimate();
  }, [location, latitude, longitude, loadClimate]);

  const handleDownloadCSV = () => {
    if (!climate || !climate.data) return;
    const headers = 'Location,Latitude,Longitude,Month,Average Temperature (C),Maximum Temperature (C),Minimum Temperature (C),Total Precipitation (mm),Rain Days,Historical Period,Data Source\n';
    const rows = climate.data.map(p => 
      `"${climate.location_name.replace(/"/g, '""')}",${climate.latitude},${climate.longitude},"${p.label}",${p.avg_temperature},${p.max_temperature},${p.min_temperature},${p.total_rainfall},${p.rainfall_days},"${climate.historical_period || climate.period}","${climate.source}"`
    ).join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `climate_data_${location.replace(/[^a-zA-Z0-9]/g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadJSON = () => {
    if (!climate) return;
    const exportData = {
      location: {
        name: climate.location_name,
        latitude: climate.latitude,
        longitude: climate.longitude,
        city: climate.city || null,
        state: climate.state || null,
        country: climate.country || null
      },
      historical_period: climate.historical_period || climate.period,
      statistics: {
        mean_annual_temperature_c: climate.annual_mean_temp,
        annual_total_precipitation_mm: climate.annual_total_rainfall,
        wettest_month: climate.wettest_month || climate.data.reduce((max, p) => p.total_rainfall > max.total_rainfall ? p : max, climate.data[0])?.label,
        warmest_month: climate.warmest_month || climate.data.reduce((max, p) => p.avg_temperature > max.avg_temperature ? p : max, climate.data[0])?.label,
        rain_day_threshold_mm: climate.rain_day_threshold_mm || 1.0
      },
      monthly_data: climate.data,
      source: climate.source,
      generated_at: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `climate_data_${location.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Dynamic values derived strictly from verified data
  const wettestMonthName = climate?.wettest_month || 
    (climate?.data ? climate.data.reduce((max, p) => p.total_rainfall > max.total_rainfall ? p : max, climate.data[0])?.label : null);
  
  const warmestMonthName = climate?.warmest_month || 
    (climate?.data ? climate.data.reduce((max, p) => p.avg_temperature > max.avg_temperature ? p : max, climate.data[0])?.label : null);

  // Dynamic chart scales for temperature
  const minTempInData = climate?.data ? Math.min(...climate.data.map(d => d.min_temperature)) : 0;
  const maxTempInData = climate?.data ? Math.max(...climate.data.map(d => d.max_temperature)) : 40;
  const tempChartBaseMin = Math.floor(Math.min(0, minTempInData) / 5) * 5;
  const tempChartBaseMax = Math.ceil(Math.max(35, maxTempInData) / 5) * 5;
  const tempChartRange = Math.max(15, tempChartBaseMax - tempChartBaseMin);

  // Dynamic chart scale for precipitation
  const maxRainInData = climate?.data ? Math.max(...climate.data.map(d => d.total_rainfall), 20) : 100;

  return (
    <div className="space-y-5">
      {/* Header & Export Controls */}
      <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary-400" />
            <h2 className="text-lg font-bold">Meteorological Research & Climate Trends</h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Verified monthly climatological normals & statistical anomalies for {location}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadCSV}
            disabled={!climate || loading}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold text-white border border-slate-700 flex items-center gap-1.5 transition"
            title="Export CSV of verified climate dataset"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" /> Export CSV
          </button>
          <button
            onClick={handleDownloadJSON}
            disabled={!climate || loading}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold text-white border border-slate-700 flex items-center gap-1.5 transition"
            title="Export JSON of verified climate dataset"
          >
            <Download className="w-3.5 h-3.5 text-primary-400" /> Export JSON
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-white dark:bg-slate-900 rounded-xl p-10 border border-slate-200 dark:border-slate-800 shadow-sm text-center flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-7 h-7 text-primary-500 animate-spin" />
          <div>
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
              Loading climate data for {location}...
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Retrieving location-specific ECMWF ERA5 reanalysis for coordinates ({latitude.toFixed(3)}°, {longitude.toFixed(3)}°)
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl p-6 text-center flex flex-col items-center justify-center gap-3">
          <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
          <div>
            <h3 className="text-sm font-bold text-red-900 dark:text-red-200">
              Climate data temporarily unavailable.
            </h3>
            <p className="text-xs text-red-700 dark:text-red-300 mt-1">
              Historical reanalysis could not be computed for the requested coordinates. Please check your connection or retry.
            </p>
          </div>
          <button
            onClick={loadClimate}
            className="mt-2 px-4 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      )}

      {/* Verified Content Display */}
      {!loading && !error && climate && (
        <>
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-400">Mean Annual Temp</span>
              <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                {climate.annual_mean_temp.toFixed(1)}°C
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Historical multi-year average</p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-400">Annual Total Precipitation</span>
              <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                {climate.annual_total_rainfall.toFixed(1)} mm
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Annual cumulative precipitation</p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-400">Wettest Month</span>
              <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                {wettestMonthName}
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Peak rainfall cycle</p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-xs text-slate-400">Warmest Month</span>
              <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                {warmestMonthName}
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">Peak temperature cycle</p>
            </div>
          </div>

          {/* Clean SVG Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Temperature Trend Chart */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 tracking-wider flex items-center gap-1.5">
                  <Thermometer className="w-4 h-4 text-amber-500" /> Monthly Temperature Cycle (°C)
                </h3>
                <span className="text-[10px] text-slate-400">Avg / Max / Min normals</span>
              </div>
              <div className="h-48 flex items-end gap-1.5 sm:gap-2 pt-6 pb-2 border-b border-slate-100 dark:border-slate-800">
                {climate.data.map((p, idx) => {
                  const heightPct = Math.min(100, Math.max(12, ((p.avg_temperature - tempChartBaseMin) / tempChartRange) * 100));
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
                      <div className="opacity-0 group-hover:opacity-100 transition pointer-events-none absolute -top-12 left-1/2 -translate-x-1/2 text-[10px] bg-slate-900 text-white px-2 py-1 rounded shadow-lg whitespace-nowrap z-30 flex flex-col items-center">
                        <span className="font-bold">{p.label}</span>
                        <span>Avg: {p.avg_temperature}°C</span>
                        <span className="text-slate-300 text-[9px]">Max: {p.max_temperature}°C | Min: {p.min_temperature}°C</span>
                      </div>
                      <div
                        style={{ height: `${heightPct}%` }}
                        className="w-full rounded-t bg-amber-500 group-hover:bg-amber-600 transition"
                      />
                      <span className="text-[9px] sm:text-[10px] text-slate-400 mt-1 truncate">{p.label.substring(0, 3)}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Rainfall Trend Chart */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 tracking-wider flex items-center gap-1.5">
                  <Droplets className="w-4 h-4 text-blue-500" /> Monthly Precipitation Distribution (mm)
                </h3>
                <span className="text-[10px] text-slate-400">Total mm / Rain days</span>
              </div>
              <div className="h-48 flex items-end gap-1.5 sm:gap-2 pt-6 pb-2 border-b border-slate-100 dark:border-slate-800">
                {climate.data.map((p, idx) => {
                  const heightPct = Math.min(100, Math.max(8, (p.total_rainfall / maxRainInData) * 100));
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
                      <div className="opacity-0 group-hover:opacity-100 transition pointer-events-none absolute -top-10 left-1/2 -translate-x-1/2 text-[10px] bg-slate-900 text-white px-2 py-1 rounded shadow-lg whitespace-nowrap z-30 flex flex-col items-center">
                        <span className="font-bold">{p.label}</span>
                        <span>{p.total_rainfall} mm</span>
                        <span className="text-blue-300 text-[9px]">{p.rainfall_days} rain days</span>
                      </div>
                      <div
                        style={{ height: `${heightPct}%` }}
                        className="w-full rounded-t bg-blue-500 group-hover:bg-blue-600 transition"
                      />
                      <span className="text-[9px] sm:text-[10px] text-slate-400 mt-1 truncate">{p.label.substring(0, 3)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Raw Tabular Data */}
          <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-x-auto">
            <h3 className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 tracking-wider mb-3 flex items-center gap-1.5">
              <Table className="w-4 h-4" /> Comprehensive Climatological Matrix
            </h3>
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400">
                  <th className="py-2.5 px-3 font-semibold">Month</th>
                  <th className="py-2.5 px-3 font-semibold">Avg Temp (°C)</th>
                  <th className="py-2.5 px-3 font-semibold">Max Temp (°C)</th>
                  <th className="py-2.5 px-3 font-semibold">Min Temp (°C)</th>
                  <th className="py-2.5 px-3 font-semibold">Total Rain (mm)</th>
                  <th className="py-2.5 px-3 font-semibold">Rain Days</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {climate.data.map((p, idx) => {
                  const isWettest = p.label === wettestMonthName;
                  const isWarmest = p.label === warmestMonthName;
                  return (
                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-850 transition">
                      <td className="py-2.5 px-3 font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                        <span>{p.label}</span>
                        {isWettest && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-normal">
                            Wettest
                          </span>
                        )}
                        {isWarmest && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-normal">
                            Warmest
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-slate-600 dark:text-slate-300">{p.avg_temperature.toFixed(1)}</td>
                      <td className="py-2.5 px-3 text-red-600 dark:text-red-400">{p.max_temperature.toFixed(1)}</td>
                      <td className="py-2.5 px-3 text-blue-600 dark:text-blue-400">{p.min_temperature.toFixed(1)}</td>
                      <td className="py-2.5 px-3 font-medium text-slate-800 dark:text-slate-200">{p.total_rainfall.toFixed(1)}</td>
                      <td className="py-2.5 px-3 text-slate-500">{p.rainfall_days}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Data Source & Attribution Section (Section 11 & 12) */}
          <div className="bg-slate-50 dark:bg-slate-900/60 p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 space-y-1.5">
            <div className="flex items-center gap-1.5 font-semibold text-slate-700 dark:text-slate-300">
              <ShieldCheck className="w-4 h-4 text-primary-500" />
              <span>Attribution & Climatological Metadata</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1 text-[11px]">
              <div>
                <span className="text-slate-400 block">Data Source:</span>
                <span className="text-slate-700 dark:text-slate-200 font-medium">{climate.source}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Historical Period:</span>
                <span className="text-slate-700 dark:text-slate-200 font-medium">
                  {climate.historical_period || climate.period}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block">Coordinates & Location:</span>
                <span className="text-slate-700 dark:text-slate-200 font-medium">
                  {climate.latitude.toFixed(4)}°N, {climate.longitude.toFixed(4)}°E ({climate.location_name})
                </span>
              </div>
              <div>
                <span className="text-slate-400 block">Rain Day Standard & Updated:</span>
                <span className="text-slate-700 dark:text-slate-200 font-medium">
                  ≥ {climate.rain_day_threshold_mm || 1.0} mm | {climate.updated_at}
                </span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
