import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { api } from '../../services/api';
import {
  HistoricalYearResponse,
  HistoricalYearMonthly,
  HistoricalYearSummary
} from '../../types';
import {
  BarChart3,
  Download,
  Thermometer,
  Droplets,
  Table,
  FileSpreadsheet,
  RefreshCw,
  AlertTriangle,
  MapPin,
  ShieldCheck,
  Info,
  Calendar,
  Layers,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  GitCompare,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const AVAILABLE_YEARS = [
  2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015,
  2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005,
  2004, 2003, 2002, 2001, 2000
];

export const ResearcherAnalytics: React.FC = () => {
  const { location, latitude, longitude } = useWeather();

  // Core State: Location + Year
  const [selectedYear, setSelectedYear] = useState<number>(2023);
  const [data, setData] = useState<HistoricalYearResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Optional Compare Years State
  const [isCompareMode, setIsCompareMode] = useState<boolean>(false);
  const [compareYear, setCompareYear] = useState<number>(2022);
  const [compareData, setCompareData] = useState<HistoricalYearResponse | null>(null);
  const [compareLoading, setCompareLoading] = useState<boolean>(false);

  // Optional Climatological Normal Expand/Collapse
  const [showNormalBenchmark, setShowNormalBenchmark] = useState<boolean>(false);

  // Interactive Hover in Charts
  const [hoveredMonthIdx, setHoveredMonthIdx] = useState<number | null>(null);

  // Load Primary Year Data
  const loadYearData = useCallback(async (yearToLoad: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getHistoricalClimateYear(location, yearToLoad, latitude, longitude);
      if (!res || !res.monthly || !Array.isArray(res.monthly) || res.monthly.length !== 12) {
        throw new Error(`Incomplete meteorological records received for year ${yearToLoad}.`);
      }
      setData(res);
    } catch (err: any) {
      console.error(`Historical load failed for year ${yearToLoad}:`, err);
      setData(null);
      setError(err?.message || `Unable to retrieve historical climate data for year ${yearToLoad}.`);
    } finally {
      setLoading(false);
    }
  }, [location, latitude, longitude]);

  // Load Comparison Year Data when compare mode is on
  const loadCompareYearData = useCallback(async (compYear: number) => {
    if (!isCompareMode) return;
    setCompareLoading(true);
    try {
      const res = await api.getHistoricalClimateYear(location, compYear, latitude, longitude);
      setCompareData(res);
    } catch (err) {
      console.error(`Comparison load failed for year ${compYear}:`, err);
      setCompareData(null);
    } finally {
      setCompareLoading(false);
    }
  }, [location, latitude, longitude, isCompareMode]);

  // Trigger when location or selectedYear changes
  useEffect(() => {
    setData(null);
    loadYearData(selectedYear);
  }, [location, latitude, longitude, selectedYear, loadYearData]);

  // Trigger compare load when compare mode or compareYear changes
  useEffect(() => {
    if (isCompareMode) {
      loadCompareYearData(compareYear);
    } else {
      setCompareData(null);
    }
  }, [isCompareMode, compareYear, loadCompareYearData]);

  const monthlyPoints = useMemo(() => data?.monthly || [], [data]);
  const summary = useMemo(() => data?.summary || null, [data]);
  const source = useMemo(() => data?.source || null, [data]);

  // Export CSV for Selected Year
  const handleDownloadCSV = () => {
    if (!data || !monthlyPoints.length) return;

    const metadataLines = [
      `# WEATHERGPT HISTORICAL METEOROLOGICAL REPORT`,
      `# Selected Year,${data.year}`,
      `# Location,"${(data.location.name || location).replace(/"/g, '""')}"`,
      `# Latitude,${data.location.latitude}`,
      `# Longitude,${data.location.longitude}`,
      `# Reference Station,"${(source?.station || 'Regional IMD Observatory').replace(/"/g, '""')}"`,
      `# Station Distance,${source?.distance_km !== undefined ? source.distance_km.toFixed(1) + ' km' : 'N/A'}`,
      `# Data Source,"${source?.name || 'India Meteorological Department (IMD) / ECMWF ERA5'}"`,
      `# Observation Coverage,January–December ${data.year}`,
      `# Annual Average Temperature,${summary?.annual_average_temperature} C`,
      `# Annual Total Rainfall,${summary?.annual_rainfall} mm`,
      `# Peak High Temperature,${summary?.highest_temperature} C`,
      `# Lowest Temperature,${summary?.lowest_temperature} C`,
      `# Total Rainy Days,${summary?.total_rainy_days} days (>= 2.5 mm)`,
      `# Rain Day Definition,"Daily precipitation >= 2.5 mm (Official IMD Standard)"`,
      `# Exported At,"${new Date().toISOString()}"`,
      ``
    ].join('\n');

    const headers = 'Month,Average Temperature (C),Maximum Temperature (C),Minimum Temperature (C),Rainfall (mm),Rainy Days (>=2.5mm)\n';
    const rows = monthlyPoints.map(p =>
      `"${p.month}",${p.avg_temperature},${p.max_temperature},${p.min_temperature},${p.rainfall},${p.rainy_days}`
    ).join('\n');

    const blob = new Blob([metadataLines + headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Historical_Climate_${(location).replace(/[^a-zA-Z0-9]/g, '_')}_${data.year}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Export JSON for Selected Year
  const handleDownloadJSON = () => {
    if (!data) return;
    const exportData = {
      selected_year: data.year,
      location: data.location,
      reference_station: {
        station: source?.station,
        distance_km: source?.distance_km
      },
      source: source,
      summary: summary,
      monthly: monthlyPoints,
      exported_at: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Historical_Climate_${(location).replace(/[^a-zA-Z0-9]/g, '_')}_${data.year}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Temperature Chart SVG Calculations
  const tempChartConfig = useMemo(() => {
    if (!monthlyPoints.length) return null;
    const allTemps = monthlyPoints.flatMap(m => [m.avg_temperature, m.max_temperature, m.min_temperature]);
    if (compareData?.monthly) {
      allTemps.push(...compareData.monthly.flatMap(m => [m.avg_temperature, m.max_temperature, m.min_temperature]));
    }
    const minVal = Math.floor(Math.min(...allTemps) / 5) * 5;
    const maxVal = Math.ceil(Math.max(...allTemps) / 5) * 5;
    const range = Math.max(10, maxVal - minVal);

    const width = 740;
    const height = 240;
    const padLeft = 45;
    const padRight = 25;
    const padTop = 20;
    const padBottom = 40;

    const plotWidth = width - padLeft - padRight;
    const plotHeight = height - padTop - padBottom;

    const getY = (val: number) => padTop + plotHeight - ((val - minVal) / range) * plotHeight;
    const getX = (idx: number) => padLeft + (idx / 11) * plotWidth;

    const maxPoints = monthlyPoints.map((m, idx) => ({ x: getX(idx), y: getY(m.max_temperature), val: m.max_temperature }));
    const avgPoints = monthlyPoints.map((m, idx) => ({ x: getX(idx), y: getY(m.avg_temperature), val: m.avg_temperature }));
    const minPoints = monthlyPoints.map((m, idx) => ({ x: getX(idx), y: getY(m.min_temperature), val: m.min_temperature }));

    const maxLineD = maxPoints.reduce((acc, p, idx) => idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '');
    const avgLineD = avgPoints.reduce((acc, p, idx) => idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '');
    const minLineD = minPoints.reduce((acc, p, idx) => idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '');

    const areaD = maxPoints.reduce((acc, p, idx) => idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '') +
      minPoints.slice().reverse().reduce((acc, p) => `${acc} L ${p.x} ${p.y}`, '') + ' Z';

    // Comparison points if active
    let compAvgLineD = '';
    if (compareData?.monthly && compareData.monthly.length === 12) {
      const compAvgPts = compareData.monthly.map((m, idx) => ({ x: getX(idx), y: getY(m.avg_temperature) }));
      compAvgLineD = compAvgPts.reduce((acc, p, idx) => idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '');
    }

    const step = range > 30 ? 10 : 5;
    const ticks: number[] = [];
    for (let t = minVal; t <= maxVal; t += step) {
      ticks.push(t);
    }

    return {
      width, height, padLeft, padRight, padTop, padBottom,
      minVal, maxVal, ticks, getY, getX,
      maxPoints, avgPoints, minPoints,
      maxLineD, avgLineD, minLineD, areaD, compAvgLineD
    };
  }, [monthlyPoints, compareData]);

  // Rainfall Chart SVG Calculations
  const rainChartConfig = useMemo(() => {
    if (!monthlyPoints.length) return null;
    const allRains = monthlyPoints.map(m => m.rainfall);
    if (compareData?.monthly) allRains.push(...compareData.monthly.map(m => m.rainfall));
    const maxRain = Math.max(...allRains, 50);
    const maxRainNice = Math.ceil(maxRain / 50) * 50;

    const allDays = monthlyPoints.map(m => m.rainy_days);
    if (compareData?.monthly) allDays.push(...compareData.monthly.map(m => m.rainy_days));
    const maxDays = Math.max(...allDays, 15);
    const maxDaysNice = Math.ceil(maxDays / 5) * 5;

    const width = 740;
    const height = 240;
    const padLeft = 50;
    const padRight = 50;
    const padTop = 20;
    const padBottom = 40;

    const plotWidth = width - padLeft - padRight;
    const plotHeight = height - padTop - padBottom;

    const slotWidth = plotWidth / 12;
    const barWidth = isCompareMode ? Math.min(15, slotWidth * 0.35) : Math.min(28, slotWidth * 0.55);

    const getYRain = (val: number) => padTop + plotHeight - (val / maxRainNice) * plotHeight;
    const getYDays = (val: number) => padTop + plotHeight - (val / maxDaysNice) * plotHeight;
    const getX = (idx: number) => padLeft + idx * slotWidth + slotWidth / 2;

    const daysPoints = monthlyPoints.map((m, idx) => ({
      x: getX(idx),
      y: getYDays(m.rainy_days),
      val: m.rainy_days
    }));
    const daysLineD = daysPoints.reduce((acc, p, idx) => idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '');

    const rainTicks = [0, Math.round(maxRainNice * 0.25), Math.round(maxRainNice * 0.5), Math.round(maxRainNice * 0.75), maxRainNice];
    const daysTicks = [0, Math.round(maxDaysNice * 0.5), maxDaysNice];

    return {
      width, height, padLeft, padRight, padTop, padBottom,
      maxRainNice, maxDaysNice, slotWidth, barWidth,
      getYRain, getYDays, getX, daysPoints, daysLineD,
      rainTicks, daysTicks
    };
  }, [monthlyPoints, compareData, isCompareMode]);

  return (
    <div className="space-y-6">
      {/* Top Header with Location, Year Selector, and Actions */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-5">
        <div className="space-y-2">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-primary-500/20 border border-primary-500/30 flex items-center justify-center text-primary-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold tracking-tight">Location & Year Historical Climate Analysis</h2>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-primary-500/20 text-primary-300 border border-primary-500/30">
                  Annual Meteorological Record
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Verified historical meteorological observations for {location} during the calendar year {selectedYear}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 pt-1">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-primary-400" />
              Location: <strong className="text-slate-200">{location}</strong> ({latitude.toFixed(4)}°N, {longitude.toFixed(4)}°E)
            </span>
            {source && (
              <span className="flex items-center gap-1">
                <ArrowRight className="w-3 h-3 text-slate-500" />
                Nearest IMD Station: <strong className="text-slate-200">{source.station}</strong> ({source.distance_km.toFixed(1)} km away)
              </span>
            )}
          </div>
        </div>

        {/* Year Selector & Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Year Picker Dropdown */}
          <div className="flex items-center gap-2 bg-slate-800/90 border border-slate-700 px-3.5 py-1.5 rounded-xl shadow-sm">
            <Calendar className="w-4 h-4 text-primary-400" />
            <label htmlFor="climate-year-select" className="text-xs text-slate-300 font-semibold">Year:</label>
            <select
              id="climate-year-select"
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              disabled={loading}
              className="bg-transparent text-white font-bold text-sm focus:outline-none cursor-pointer pr-1"
            >
              {AVAILABLE_YEARS.map(y => (
                <option key={y} value={y} className="bg-slate-900 text-white">
                  {y}
                </option>
              ))}
            </select>
          </div>

          {/* Compare Years Toggle */}
          <button
            onClick={() => setIsCompareMode(!isCompareMode)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border transition shadow-sm ${
              isCompareMode
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
            }`}
          >
            <GitCompare className="w-3.5 h-3.5" />
            {isCompareMode ? 'Comparing' : 'Compare Years'}
          </button>

          {/* Comparison Year Dropdown if Compare Mode is on */}
          {isCompareMode && (
            <div className="flex items-center gap-1.5 bg-amber-950/40 border border-amber-800/60 px-3 py-1.5 rounded-xl text-xs text-amber-200">
              <span className="text-[11px] text-amber-300/80">vs:</span>
              <select
                value={compareYear}
                onChange={(e) => setCompareYear(Number(e.target.value))}
                className="bg-transparent text-amber-200 font-bold focus:outline-none cursor-pointer"
              >
                {AVAILABLE_YEARS.filter(y => y !== selectedYear).map(y => (
                  <option key={y} value={y} className="bg-slate-900 text-white">
                    {y}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Export Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadCSV}
              disabled={!data || loading}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold text-white border border-slate-700 flex items-center gap-1.5 transition shadow-sm"
              title={`Export CSV for ${selectedYear}`}
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" /> Export CSV
            </button>
            <button
              onClick={handleDownloadJSON}
              disabled={!data || loading}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold text-white border border-slate-700 flex items-center gap-1.5 transition shadow-sm"
              title={`Export JSON for ${selectedYear}`}
            >
              <Download className="w-3.5 h-3.5 text-primary-400" /> Export JSON
            </button>
          </div>
        </div>
      </div>

      {/* Loading State per Section 12 */}
      {loading && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-12 border border-slate-200 dark:border-slate-800 shadow-sm text-center flex flex-col items-center justify-center gap-3.5">
          <div className="w-12 h-12 rounded-full bg-primary-50 dark:bg-primary-950/50 flex items-center justify-center">
            <RefreshCw className="w-6 h-6 text-primary-500 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Loading historical climate data for {selectedYear}...
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Retrieving location-specific meteorological observations for {location} ({latitude.toFixed(4)}°, {longitude.toFixed(4)}°)
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-2xl p-8 text-center flex flex-col items-center justify-center gap-3">
          <AlertTriangle className="w-9 h-9 text-red-600 dark:text-red-400" />
          <div>
            <h3 className="text-base font-bold text-red-900 dark:text-red-200">
              Unable to retrieve historical climate data.
            </h3>
            <p className="text-xs text-red-700 dark:text-red-300 mt-1 max-w-md">
              {error}
            </p>
          </div>
          <button
            onClick={() => loadYearData(selectedYear)}
            className="mt-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-semibold flex items-center gap-2 transition shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      )}

      {/* Verified Year Data Display */}
      {!loading && !error && data && summary && (
        <>
          {/* Main Section Header */}
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Historical Climate — {selectedYear}
              </h3>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                (Actual 12-month meteorological records)
              </span>
            </div>
            {isCompareMode && compareData && (
              <span className="text-xs font-medium text-amber-600 dark:text-amber-400">
                Compared against {compareYear}
              </span>
            )}
          </div>

          {/* Section 5: Summary Cards strictly calculated from the selected year's data */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
            {/* Card 1: Annual Average Temperature */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Annual Avg Temp</span>
              <div className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1.5">
                {summary.annual_average_temperature.toFixed(1)}°C
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                {selectedYear} Mean
                {isCompareMode && compareData?.summary && (
                  <span className="block text-amber-500 font-medium">
                    vs {compareYear}: {(summary.annual_average_temperature - compareData.summary.annual_average_temperature).toFixed(1)}°C
                  </span>
                )}
              </div>
            </div>

            {/* Card 2: Annual Rainfall */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Annual Rainfall</span>
              <div className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1.5">
                {summary.annual_rainfall.toFixed(1)} <span className="text-xs font-normal text-slate-400">mm</span>
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                {summary.total_rainy_days} rainy days (≥2.5mm)
                {isCompareMode && compareData?.summary && (
                  <span className="block text-blue-500 font-medium">
                    vs {compareYear}: {(summary.annual_rainfall - compareData.summary.annual_rainfall).toFixed(1)} mm
                  </span>
                )}
              </div>
            </div>

            {/* Card 3: Highest Temperature */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Highest Temp</span>
              <div className="text-2xl font-extrabold text-red-600 dark:text-red-400 mt-1.5">
                {summary.highest_temperature.toFixed(1)}°C
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Peak day in {selectedYear}</div>
            </div>

            {/* Card 4: Lowest Temperature */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Lowest Temp</span>
              <div className="text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-1.5">
                {summary.lowest_temperature.toFixed(1)}°C
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Coldest day in {selectedYear}</div>
            </div>

            {/* Card 5: Wettest Month */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Wettest Month</span>
              <div className="text-xl font-extrabold text-cyan-600 dark:text-cyan-400 mt-1.5 truncate">
                {summary.wettest_month}
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Driest: {summary.driest_month}</div>
            </div>

            {/* Card 6: Warmest Month */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Warmest Month</span>
              <div className="text-xl font-extrabold text-amber-600 dark:text-amber-400 mt-1.5 truncate">
                {summary.warmest_month}
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Coldest: {summary.coldest_month}</div>
            </div>
          </div>

          {/* Section 6: Interactive SVG Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Monthly Temperature Chart */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <Thermometer className="w-4 h-4 text-amber-500" />
                      Monthly Temperature Observations — {selectedYear} (°C)
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Average, Maximum & Minimum Temperature ({selectedYear})
                    </p>
                  </div>
                  {/* Legend */}
                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Max
                    </span>
                    <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Avg
                    </span>
                    <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Min
                    </span>
                    {isCompareMode && (
                      <span className="flex items-center gap-1.5 text-amber-400">
                        <span className="w-2.5 h-0.5 bg-amber-400 border border-dashed border-amber-300"></span> {compareYear} Avg
                      </span>
                    )}
                  </div>
                </div>

                {tempChartConfig && (
                  <div className="relative pt-2">
                    <svg
                      viewBox={`0 0 ${tempChartConfig.width} ${tempChartConfig.height}`}
                      className="w-full h-auto select-none overflow-visible"
                    >
                      <defs>
                        <linearGradient id="yearTempAreaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#ef4444" stopOpacity="0.16" />
                          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.16" />
                        </linearGradient>
                      </defs>

                      {/* Y Gridlines */}
                      {tempChartConfig.ticks.map(tick => {
                        const y = tempChartConfig.getY(tick);
                        return (
                          <g key={tick} className="text-slate-400 dark:text-slate-600">
                            <line
                              x1={tempChartConfig.padLeft}
                              y1={y}
                              x2={tempChartConfig.width - tempChartConfig.padRight}
                              y2={y}
                              stroke="currentColor"
                              strokeDasharray="4 4"
                              strokeWidth="0.8"
                              opacity="0.4"
                            />
                            <text
                              x={tempChartConfig.padLeft - 8}
                              y={y + 3.5}
                              textAnchor="end"
                              fontSize="10"
                              fill="currentColor"
                            >
                              {tick}°C
                            </text>
                          </g>
                        );
                      })}

                      {/* Shaded Diurnal Envelope between Max and Min */}
                      <path d={tempChartConfig.areaD} fill="url(#yearTempAreaGrad)" />

                      {/* Comparison year line if present */}
                      {isCompareMode && tempChartConfig.compAvgLineD && (
                        <path
                          d={tempChartConfig.compAvgLineD}
                          fill="none"
                          stroke="#fbbf24"
                          strokeWidth="2"
                          strokeDasharray="4 3"
                        />
                      )}

                      {/* Main Year Lines */}
                      <path d={tempChartConfig.maxLineD} fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" />
                      <path d={tempChartConfig.avgLineD} fill="none" stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round" />
                      <path d={tempChartConfig.minLineD} fill="none" stroke="#3b82f6" strokeWidth="2.5" strokeLinecap="round" />

                      {/* Hover column marker */}
                      {hoveredMonthIdx !== null && (
                        <line
                          x1={tempChartConfig.getX(hoveredMonthIdx)}
                          y1={tempChartConfig.padTop}
                          x2={tempChartConfig.getX(hoveredMonthIdx)}
                          y2={tempChartConfig.height - tempChartConfig.padBottom}
                          stroke="#94a3b8"
                          strokeWidth="1.5"
                          strokeDasharray="3 3"
                        />
                      )}

                      {/* Dots & month labels */}
                      {monthlyPoints.map((m, idx) => {
                        const x = tempChartConfig.getX(idx);
                        const isHovered = hoveredMonthIdx === idx;
                        const maxPt = tempChartConfig.maxPoints[idx];
                        const avgPt = tempChartConfig.avgPoints[idx];
                        const minPt = tempChartConfig.minPoints[idx];

                        return (
                          <g
                            key={idx}
                            onMouseEnter={() => setHoveredMonthIdx(idx)}
                            onMouseLeave={() => setHoveredMonthIdx(null)}
                            className="cursor-pointer"
                          >
                            <text
                              x={x}
                              y={tempChartConfig.height - tempChartConfig.padBottom + 18}
                              textAnchor="middle"
                              fontSize="10"
                              fontWeight={isHovered ? 'bold' : 'normal'}
                              fill={isHovered ? '#f59e0b' : '#94a3b8'}
                            >
                              {m.month.substring(0, 3)}
                            </text>

                            <circle cx={maxPt.x} cy={maxPt.y} r={isHovered ? 5.5 : 3.5} fill="#ef4444" stroke="#ffffff" strokeWidth="1.5" />
                            <circle cx={avgPt.x} cy={avgPt.y} r={isHovered ? 5.5 : 3.5} fill="#f59e0b" stroke="#ffffff" strokeWidth="1.5" />
                            <circle cx={minPt.x} cy={minPt.y} r={isHovered ? 5.5 : 3.5} fill="#3b82f6" stroke="#ffffff" strokeWidth="1.5" />

                            <rect
                              x={x - (tempChartConfig.width / 24)}
                              y={tempChartConfig.padTop}
                              width={tempChartConfig.width / 12}
                              height={tempChartConfig.height - tempChartConfig.padTop - tempChartConfig.padBottom}
                              fill="transparent"
                            />
                          </g>
                        );
                      })}
                    </svg>

                    {/* Tooltip Overlay */}
                    {hoveredMonthIdx !== null && monthlyPoints[hoveredMonthIdx] && (
                      <div className="mt-3 p-3 rounded-xl bg-slate-900 text-white text-xs border border-slate-800 flex items-center justify-between shadow-lg">
                        <span className="font-bold text-slate-200">
                          {monthlyPoints[hoveredMonthIdx].month} {selectedYear}:
                        </span>
                        <div className="flex items-center gap-4">
                          <span className="text-amber-400">
                            Avg: <strong>{monthlyPoints[hoveredMonthIdx].avg_temperature}°C</strong>
                          </span>
                          <span className="text-red-400">
                            Max: <strong>{monthlyPoints[hoveredMonthIdx].max_temperature}°C</strong>
                          </span>
                          <span className="text-blue-400">
                            Min: <strong>{monthlyPoints[hoveredMonthIdx].min_temperature}°C</strong>
                          </span>
                          {isCompareMode && compareData?.monthly && compareData.monthly[hoveredMonthIdx] && (
                            <span className="text-amber-300 pl-2 border-l border-slate-700">
                              {compareYear} Avg: {compareData.monthly[hoveredMonthIdx].avg_temperature}°C
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="text-[11px] text-slate-400 mt-2 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-2">
                <span>X-Axis: All 12 Months of {selectedYear}</span>
                <span>Y-Axis: Temperature (°C)</span>
              </div>
            </div>

            {/* Monthly Rainfall Chart */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <Droplets className="w-4 h-4 text-blue-500" />
                      Monthly Rainfall Observations — {selectedYear} (mm)
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Actual Total Monthly Rainfall & Rainy Days ({selectedYear})
                    </p>
                  </div>
                  {/* Legend */}
                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                      <span className="w-2.5 h-2.5 rounded bg-blue-500"></span> {selectedYear} (mm)
                    </span>
                    {isCompareMode && (
                      <span className="flex items-center gap-1.5 text-amber-400">
                        <span className="w-2.5 h-2.5 rounded bg-amber-500"></span> {compareYear} (mm)
                      </span>
                    )}
                    <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Rainy Days (≥2.5mm)
                    </span>
                  </div>
                </div>

                {rainChartConfig && (
                  <div className="relative pt-2">
                    <svg
                      viewBox={`0 0 ${rainChartConfig.width} ${rainChartConfig.height}`}
                      className="w-full h-auto select-none overflow-visible"
                    >
                      <defs>
                        <linearGradient id="yearRainBarGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#0284c7" />
                          <stop offset="100%" stopColor="#38bdf8" />
                        </linearGradient>
                        <linearGradient id="compRainBarGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#d97706" />
                          <stop offset="100%" stopColor="#f59e0b" />
                        </linearGradient>
                      </defs>

                      {/* Left Y Axis gridlines (mm) */}
                      {rainChartConfig.rainTicks.map(tick => {
                        const y = rainChartConfig.getYRain(tick);
                        return (
                          <g key={tick} className="text-slate-400 dark:text-slate-600">
                            <line
                              x1={rainChartConfig.padLeft}
                              y1={y}
                              x2={rainChartConfig.width - rainChartConfig.padRight}
                              y2={y}
                              stroke="currentColor"
                              strokeDasharray="4 4"
                              strokeWidth="0.8"
                              opacity="0.4"
                            />
                            <text
                              x={rainChartConfig.padLeft - 8}
                              y={y + 3.5}
                              textAnchor="end"
                              fontSize="10"
                              fill="currentColor"
                            >
                              {tick}
                            </text>
                          </g>
                        );
                      })}

                      {/* Right Y Axis labels (rain days) */}
                      {rainChartConfig.daysTicks.map(tick => {
                        const y = rainChartConfig.getYDays(tick);
                        return (
                          <g key={tick} className="text-amber-500/80">
                            <text
                              x={rainChartConfig.width - rainChartConfig.padRight + 8}
                              y={y + 3.5}
                              textAnchor="start"
                              fontSize="10"
                              fill="currentColor"
                            >
                              {tick}d
                            </text>
                          </g>
                        );
                      })}

                      {/* Bars */}
                      {monthlyPoints.map((m, idx) => {
                        const x = rainChartConfig.getX(idx);
                        const isHovered = hoveredMonthIdx === idx;
                        const barH = Math.max(3, (m.rainfall / rainChartConfig.maxRainNice) * (rainChartConfig.height - rainChartConfig.padTop - rainChartConfig.padBottom));
                        const y = rainChartConfig.getYRain(m.rainfall);

                        // Comparison bar offset if compare mode
                        const barX = isCompareMode ? x - rainChartConfig.barWidth - 1 : x - rainChartConfig.barWidth / 2;

                        let compBar = null;
                        if (isCompareMode && compareData?.monthly && compareData.monthly[idx]) {
                          const compM = compareData.monthly[idx];
                          const compH = Math.max(3, (compM.rainfall / rainChartConfig.maxRainNice) * (rainChartConfig.height - rainChartConfig.padTop - rainChartConfig.padBottom));
                          const compY = rainChartConfig.getYRain(compM.rainfall);
                          compBar = (
                            <rect
                              x={x + 1}
                              y={compY}
                              width={rainChartConfig.barWidth}
                              height={compH}
                              rx="3"
                              fill="url(#compRainBarGrad)"
                              opacity={isHovered ? 1 : 0.8}
                            />
                          );
                        }

                        return (
                          <g
                            key={idx}
                            onMouseEnter={() => setHoveredMonthIdx(idx)}
                            onMouseLeave={() => setHoveredMonthIdx(null)}
                            className="cursor-pointer"
                          >
                            <rect
                              x={barX}
                              y={y}
                              width={rainChartConfig.barWidth}
                              height={barH}
                              rx="3"
                              fill="url(#yearRainBarGrad)"
                              opacity={isHovered ? 1 : 0.88}
                            />
                            {compBar}

                            {/* X Month Label */}
                            <text
                              x={x}
                              y={rainChartConfig.height - rainChartConfig.padBottom + 18}
                              textAnchor="middle"
                              fontSize="10"
                              fontWeight={isHovered ? 'bold' : 'normal'}
                              fill={isHovered ? '#0284c7' : '#94a3b8'}
                            >
                              {m.month.substring(0, 3)}
                            </text>
                          </g>
                        );
                      })}

                      {/* Rainy Days Trendline Overlay */}
                      <path
                        d={rainChartConfig.daysLineD}
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth="2.2"
                        strokeDasharray="4 2"
                      />

                      {rainChartConfig.daysPoints.map((p, idx) => (
                        <circle
                          key={idx}
                          cx={p.x}
                          cy={p.y}
                          r={hoveredMonthIdx === idx ? 5 : 3.5}
                          fill="#f59e0b"
                          stroke="#ffffff"
                          strokeWidth="1.5"
                        />
                      ))}
                    </svg>

                    {/* Tooltip Overlay */}
                    {hoveredMonthIdx !== null && monthlyPoints[hoveredMonthIdx] && (
                      <div className="mt-3 p-3 rounded-xl bg-slate-900 text-white text-xs border border-slate-800 flex items-center justify-between shadow-lg">
                        <span className="font-bold text-slate-200">
                          {monthlyPoints[hoveredMonthIdx].month} {selectedYear} Rainfall:
                        </span>
                        <div className="flex items-center gap-4">
                          <span className="text-blue-400">
                            Rainfall: <strong>{monthlyPoints[hoveredMonthIdx].rainfall} mm</strong>
                          </span>
                          <span className="text-amber-400">
                            Rain Days (≥2.5mm): <strong>{monthlyPoints[hoveredMonthIdx].rainy_days} days</strong>
                          </span>
                          {isCompareMode && compareData?.monthly && compareData.monthly[hoveredMonthIdx] && (
                            <span className="text-amber-300 pl-2 border-l border-slate-700">
                              {compareYear}: {compareData.monthly[hoveredMonthIdx].rainfall} mm
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="text-[11px] text-slate-400 mt-2 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-2">
                <span>Left Y-Axis: Rainfall (mm)</span>
                <span>Right Y-Axis: Rainy Days (days/month)</span>
              </div>
            </div>
          </div>

          {/* Section 4: 12-Month Meteorological Observations Table */}
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-x-auto">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <Table className="w-4 h-4 text-primary-500" />
                  Monthly Meteorological Observations Table — {selectedYear}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Actual recorded values for each calendar month of {selectedYear}
                </p>
              </div>
              <span className="text-xs text-slate-400">
                Location: <strong>{location}</strong> | Year: <strong className="text-primary-400">{selectedYear}</strong>
              </span>
            </div>

            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400">
                  <th className="py-3 px-3.5 font-semibold">Month</th>
                  <th className="py-3 px-3.5 font-semibold">Avg Temp (°C)</th>
                  <th className="py-3 px-3.5 font-semibold">Max Temp (°C)</th>
                  <th className="py-3 px-3.5 font-semibold">Min Temp (°C)</th>
                  <th className="py-3 px-3.5 font-semibold">Rainfall (mm)</th>
                  <th className="py-3 px-3.5 font-semibold">Rainy Days (≥2.5mm)</th>
                  <th className="py-3 px-3.5 font-semibold">Season / Context</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {monthlyPoints.map((p, idx) => {
                  const isWettest = p.month === summary.wettest_month;
                  const isWarmest = p.month === summary.warmest_month;

                  let seasonLabel = 'Post-Monsoon';
                  if (['December', 'January', 'February'].includes(p.month)) seasonLabel = 'Winter / Cold Season';
                  else if (['March', 'April', 'May'].includes(p.month)) seasonLabel = 'Pre-Monsoon / Summer';
                  else if (['June', 'July', 'August', 'September'].includes(p.month)) seasonLabel = 'SW Monsoon';

                  return (
                    <tr
                      key={idx}
                      className={`transition ${
                        hoveredMonthIdx === idx
                          ? 'bg-primary-50/50 dark:bg-primary-950/20'
                          : 'hover:bg-slate-50 dark:hover:bg-slate-800/40'
                      }`}
                      onMouseEnter={() => setHoveredMonthIdx(idx)}
                      onMouseLeave={() => setHoveredMonthIdx(null)}
                    >
                      <td className="py-3 px-3.5 font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                        <span>{p.month}</span>
                        {isWettest && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-semibold">
                            Wettest
                          </span>
                        )}
                        {isWarmest && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-semibold">
                            Warmest
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3.5 font-medium text-slate-700 dark:text-slate-300">
                        {p.avg_temperature.toFixed(1)}
                      </td>
                      <td className="py-3 px-3.5 text-red-600 dark:text-red-400 font-medium">
                        {p.max_temperature.toFixed(1)}
                      </td>
                      <td className="py-3 px-3.5 text-blue-600 dark:text-blue-400 font-medium">
                        {p.min_temperature.toFixed(1)}
                      </td>
                      <td className="py-3 px-3.5 font-bold text-slate-900 dark:text-slate-100">
                        {p.rainfall.toFixed(1)}
                      </td>
                      <td className="py-3 px-3.5 text-slate-600 dark:text-slate-400">
                        {p.rainy_days}
                      </td>
                      <td className="py-3 px-3.5 text-slate-500 text-[11px]">
                        {seasonLabel}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-slate-200 dark:border-slate-700 font-bold bg-slate-50/70 dark:bg-slate-800/30">
                  <td className="py-3 px-3.5 text-slate-900 dark:text-white">
                    ANNUAL TOTAL / STATS ({selectedYear})
                  </td>
                  <td className="py-3 px-3.5 text-slate-900 dark:text-white">
                    {summary.annual_average_temperature.toFixed(1)}°C
                  </td>
                  <td className="py-3 px-3.5 text-red-600 dark:text-red-400">
                    {summary.highest_temperature.toFixed(1)}°C (Peak)
                  </td>
                  <td className="py-3 px-3.5 text-blue-600 dark:text-blue-400">
                    {summary.lowest_temperature.toFixed(1)}°C (Lowest)
                  </td>
                  <td className="py-3 px-3.5 text-slate-900 dark:text-white">
                    {summary.annual_rainfall.toFixed(1)} mm
                  </td>
                  <td className="py-3 px-3.5 text-slate-900 dark:text-white">
                    {summary.total_rainy_days} days
                  </td>
                  <td className="py-3 px-3.5 text-slate-500 text-[11px]">
                    Calendar Year {selectedYear}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

          {/* Section 9: Data Source Information Section */}
          <div className="bg-slate-900 text-white p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <h4 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                Data Source & Meteorological Provenance
              </h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 text-xs">
              <div>
                <span className="text-slate-400 block font-medium">Data Source:</span>
                <span className="text-slate-100 font-bold text-sm mt-0.5 block">
                  {source?.name || 'India Meteorological Department (IMD) / ECMWF ERA5'}
                </span>
                <span className="text-[11px] text-slate-400 mt-0.5 block">
                  {source?.attribution || 'ECMWF Copernicus Reanalysis assimilated with IMD / Global Surface Meteorological Stations'}
                </span>
              </div>

              <div>
                <span className="text-slate-400 block font-medium">Reference Station:</span>
                <span className="text-slate-100 font-bold text-sm mt-0.5 block">
                  {source?.station || 'Regional Meteorological Station'}
                </span>
                <span className="text-[11px] text-slate-400 mt-0.5 block">
                  {source ? (
                    <>
                      Station ID: <strong className="text-slate-300">{source.station_id || 'N/A'}</strong> | Distance: <strong className="text-emerald-400">{source.distance_km.toFixed(1)} km</strong>
                    </>
                  ) : 'Active Station'}
                </span>
              </div>

              <div>
                <span className="text-slate-400 block font-medium">Selected Year & Coverage:</span>
                <span className="text-slate-100 font-bold text-sm mt-0.5 block">
                  {selectedYear} ({source?.data_coverage || `January–December ${selectedYear}`})
                </span>
                <span className="text-[11px] text-slate-400 mt-0.5 block">
                  Coordinates: {latitude.toFixed(4)}°N, {longitude.toFixed(4)}°E
                </span>
              </div>

              <div>
                <span className="text-slate-400 block font-medium">Measurement Standard:</span>
                <span className="text-slate-100 font-semibold mt-0.5 block">
                  Rain Day: Daily Precipitation ≥ 2.5 mm
                </span>
                <span className="text-[11px] text-slate-400 mt-0.5 block">
                  Official IMD Standard Definition
                </span>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-2">
              <span>
                Requested Location: <em>{location}</em> ({latitude.toFixed(4)}°, {longitude.toFixed(4)}°)
              </span>
              <span>
                Report Generated: <em>{new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })}</em>
              </span>
            </div>
          </div>

          {/* Section 8 & 15: Optional Climatological Normal Reference (1991–2020) */}
          <div className="bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-primary-500" />
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  Climatological Normal Reference Benchmark (1991–2020)
                </h4>
                <span className="text-xs text-slate-400">
                  (Official IMD 30-Year Baseline)
                </span>
              </div>
              <button
                onClick={() => setShowNormalBenchmark(!showNormalBenchmark)}
                className="px-3 py-1 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1 transition hover:bg-slate-100 dark:hover:bg-slate-750"
              >
                {showNormalBenchmark ? (
                  <>Hide Benchmark <ChevronUp className="w-3.5 h-3.5" /></>
                ) : (
                  <>Compare with 30-Year Normal <ChevronDown className="w-3.5 h-3.5" /></>
                )}
              </button>
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Do not confuse actual single-year observations ({selectedYear}) with climatological normals.
              Climatological normals represent long-term 30-year baseline averages (1991–2020) established by the
              India Meteorological Department (IMD) to evaluate climate variability.
            </p>

            {showNormalBenchmark && data.climatological_normal && (
              <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
                  <span className="text-[11px] text-slate-400 block font-medium">30-Yr Normal Mean Temp:</span>
                  <div className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
                    {data.climatological_normal.annual?.mean_temperature_c || data.climatological_normal.annual_mean_temp}°C
                  </div>
                  <span className="text-[10px] text-slate-400">1991–2020 Normal</span>
                </div>

                <div className="p-3 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
                  <span className="text-[11px] text-slate-400 block font-medium">30-Yr Normal Rainfall:</span>
                  <div className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
                    {data.climatological_normal.annual?.total_precipitation_mm || data.climatological_normal.annual_total_rainfall} mm
                  </div>
                  <span className="text-[10px] text-slate-400">1991–2020 Normal</span>
                </div>

                <div className="p-3 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
                  <span className="text-[11px] text-slate-400 block font-medium">30-Yr Wettest Month:</span>
                  <div className="text-lg font-bold text-cyan-600 dark:text-cyan-400 mt-0.5 truncate">
                    {data.climatological_normal.annual?.wettest_month || data.climatological_normal.wettest_month}
                  </div>
                  <span className="text-[10px] text-slate-400">Normal peak month</span>
                </div>

                <div className="p-3 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
                  <span className="text-[11px] text-slate-400 block font-medium">30-Yr Warmest Month:</span>
                  <div className="text-lg font-bold text-amber-600 dark:text-amber-400 mt-0.5 truncate">
                    {data.climatological_normal.annual?.warmest_month || data.climatological_normal.warmest_month}
                  </div>
                  <span className="text-[10px] text-slate-400">Normal peak month</span>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
