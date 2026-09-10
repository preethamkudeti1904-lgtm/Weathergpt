import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Clock, Wind, ArrowUp } from 'lucide-react';
import { WindPoint, degreesToCardinal } from '../../services/windService';
import { formatLocalTime, getTimezoneAbbreviation } from '../../services/timezoneService';

interface WindTimeSliderProps {
  hourlyPoints: WindPoint[];
  currentPoint: WindPoint;
  selectedIndex: number; // -1 means Live/Now, 0..N means hourly point
  onSelectIndex: (index: number) => void;
  timezone: string;
  t: (key: string) => string;
}

export const WindTimeSlider: React.FC<WindTimeSliderProps> = ({
  hourlyPoints,
  currentPoint,
  selectedIndex,
  onSelectIndex,
  timezone,
  t
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const totalSteps = hourlyPoints.length; // usually 24

  // Auto-play interval
  useEffect(() => {
    if (!isPlaying || totalSteps === 0) return;

    const interval = setInterval(() => {
      const next = selectedIndex + 1 >= totalSteps ? 0 : selectedIndex + 1;
      onSelectIndex(next);
    }, 1400);

    return () => clearInterval(interval);
  }, [isPlaying, totalSteps, selectedIndex, onSelectIndex]);

  // Format timestamp in local timezone
  const formatHourLabel = (timestamp: string): string => {
    try {
      return formatLocalTime(timestamp, timezone, false, 'en');
    } catch {
      return timestamp;
    }
  };

  const tzAbbr = getTimezoneAbbreviation(timezone);

  // Active wind point being viewed
  const activePoint = selectedIndex === -1 ? currentPoint : hourlyPoints[selectedIndex] || currentPoint;
  const isLive = selectedIndex === -1;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      {/* Slider Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-400 border border-sky-100 dark:border-sky-900/40">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <span>{t('forecast_time')}</span>
              {isLive ? (
                <span className="px-2 py-0.5 text-[11px] font-bold rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  {t('live_now')}
                </span>
              ) : (
                <span className="px-2 py-0.5 text-[11px] font-medium rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
                  +{selectedIndex + 1}h Forecast
                </span>
              )}
            </h3>
            <p className="text-xs text-slate-400">
              Scrub timeline to visualize hourly forecast wind flow &bull; {tzAbbr}
            </p>
          </div>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onSelectIndex(-1)}
            title="Reset to Live"
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 border ${
              isLive
                ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-200'
            }`}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{t('live_now')}</span>
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            title={isPlaying ? 'Pause' : 'Play Timeline'}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
              isPlaying
                ? 'bg-amber-500 text-white shadow-sm hover:bg-amber-600'
                : 'bg-sky-600 text-white shadow-sm hover:bg-sky-700'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Play 24h</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Scrub Range Slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
          <span className="font-semibold text-emerald-600 dark:text-emerald-400">
            {t('live_now')}
          </span>
          <span className="font-medium text-slate-700 dark:text-slate-300">
            {isLive ? 'Current Surface Wind' : formatHourLabel(activePoint.timestamp)}
          </span>
          <span>+24h Outlook</span>
        </div>

        <input
          type="range"
          min={-1}
          max={Math.max(totalSteps - 1, 0)}
          value={selectedIndex}
          onChange={(e) => onSelectIndex(parseInt(e.target.value, 10))}
          className="w-full h-2.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-600 transition"
        />

        <div className="flex justify-between text-[10px] text-slate-400 px-0.5">
          <span>Now</span>
          <span>+6h</span>
          <span>+12h</span>
          <span>+18h</span>
          <span>+24h</span>
        </div>
      </div>

      {/* Forecast Wind Cards Strip */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2.5">
          {t('wind_forecast')}
        </h4>

        <div className="flex gap-2.5 overflow-x-auto pb-2 pt-1 no-scrollbar scroll-smooth">
          {/* Live Card */}
          <button
            onClick={() => onSelectIndex(-1)}
            className={`flex-shrink-0 w-28 p-2.5 rounded-xl border text-left transition ${
              isLive
                ? 'bg-sky-50 dark:bg-sky-950/60 border-sky-400 dark:border-sky-500 shadow-sm ring-1 ring-sky-400'
                : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400">
                {t('live_now')}
              </span>
              <div
                className="w-5 h-5 rounded-full flex items-center justify-center bg-sky-100 dark:bg-sky-900/50 text-sky-600 dark:text-sky-400"
                style={{
                  transform: `rotate(${currentPoint.windDirection || 0}deg)`
                }}
              >
                <ArrowUp className="w-3 h-3" />
              </div>
            </div>

            <div className="text-sm font-bold text-slate-800 dark:text-slate-100">
              {currentPoint.windSpeed !== null ? `${currentPoint.windSpeed} km/h` : '--'}
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              {currentPoint.windDirectionCardinal} &bull; {currentPoint.windDirection}°
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              Gust: {currentPoint.windGust !== null ? `${currentPoint.windGust} km/h` : '--'}
            </div>
          </button>

          {/* Hourly Cards */}
          {hourlyPoints.map((point, idx) => {
            const isSelected = selectedIndex === idx;
            const hourLabel = formatHourLabel(point.timestamp);
            const cardinal = point.windDirectionCardinal || degreesToCardinal(point.windDirection);

            return (
              <button
                key={`${point.timestamp}-${idx}`}
                onClick={() => onSelectIndex(idx)}
                className={`flex-shrink-0 w-28 p-2.5 rounded-xl border text-left transition ${
                  isSelected
                    ? 'bg-sky-50 dark:bg-sky-950/60 border-sky-400 dark:border-sky-500 shadow-sm ring-1 ring-sky-400'
                    : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                    {hourLabel}
                  </span>
                  <div
                    className="w-5 h-5 rounded-full flex items-center justify-center bg-sky-100 dark:bg-sky-900/50 text-sky-600 dark:text-sky-400"
                    style={{
                      transform: `rotate(${point.windDirection || 0}deg)`
                    }}
                  >
                    <ArrowUp className="w-3 h-3" />
                  </div>
                </div>

                <div className="text-sm font-bold text-slate-800 dark:text-slate-100">
                  {point.windSpeed !== null ? `${point.windSpeed} km/h` : '--'}
                </div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  {cardinal} &bull; {point.windDirection !== null ? `${point.windDirection}°` : '--'}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  Gust: {point.windGust !== null ? `${point.windGust} km/h` : '--'}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
