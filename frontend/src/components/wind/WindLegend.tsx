import React from 'react';
import { BEAUFORT_LEVELS, BeaufortLevel } from '../../services/windService';

interface WindLegendProps {
  currentSpeed?: number | null;
  t: (key: string) => string;
}

export const WindLegend: React.FC<WindLegendProps> = ({ currentSpeed, t }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {t('wind_legend')} (WMO Beaufort Scale)
        </h4>
        <span className="text-[11px] text-slate-400">km/h</span>
      </div>

      <div className="grid grid-cols-5 gap-2">
        {BEAUFORT_LEVELS.map((level: BeaufortLevel) => {
          const isActive =
            currentSpeed !== null &&
            currentSpeed !== undefined &&
            currentSpeed >= level.minKmh &&
            (level.maxKmh === null || currentSpeed <= level.maxKmh);

          return (
            <div
              key={level.category}
              className={`flex flex-col p-2 rounded-xl transition-all border ${
                isActive
                  ? 'bg-sky-50/80 dark:bg-sky-950/40 border-sky-400 dark:border-sky-500 shadow-sm ring-1 ring-sky-400'
                  : 'bg-slate-50 dark:bg-slate-800/40 border-slate-100 dark:border-slate-800'
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: level.color }}
                />
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                  {t(level.labelKey)}
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
                {level.maxKmh ? `${level.minKmh}-${level.maxKmh}` : `≥${level.minKmh}`}
              </span>
            </div>
          );
        })}
      </div>

      <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-2.5">
        Map wind particles and arrows animate dynamically along the flow vector with velocity proportional to speed.
      </p>
    </div>
  );
};
