import React from 'react';
import { Compass as CompassIcon, Navigation2 } from 'lucide-react';
import { degreesToCardinal } from '../../services/windService';

interface WindCompassProps {
  degrees: number | null;
  speed: number | null;
  cardinal?: string | null;
  t: (key: string) => string;
}

export const WindCompass: React.FC<WindCompassProps> = ({ degrees, speed, cardinal, t }) => {
  const hasData = degrees !== null && degrees !== undefined && !isNaN(degrees);
  const normalizedDegrees = hasData ? ((degrees % 360) + 360) % 360 : 0;
  const currentCardinal = cardinal || degreesToCardinal(degrees);

  // Direction wind is blowing TOWARDS is (degrees + 180) % 360
  const blowingTowardsDegrees = (normalizedDegrees + 180) % 360;
  const blowingTowardsCardinal = degreesToCardinal(blowingTowardsDegrees);

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm flex flex-col items-center justify-between relative overflow-hidden">
      {/* Header */}
      <div className="w-full flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-950/40 text-sky-600 dark:text-sky-400 border border-sky-100 dark:border-sky-900/40">
            <CompassIcon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
              {t('wind_compass')}
            </h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">
              {t('bearing')} &bull; {hasData ? `${normalizedDegrees}°` : t('wind_data_unavailable')}
            </p>
          </div>
        </div>

        {hasData && (
          <span className="px-2.5 py-1 text-xs font-bold font-mono rounded-md bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800">
            {currentCardinal} &bull; {normalizedDegrees}°
          </span>
        )}
      </div>

      {/* Compass Dial SVG */}
      <div className="relative w-52 h-52 my-2 flex items-center justify-center select-none">
        {/* Outer Ring with Cardinal Markers */}
        <svg viewBox="0 0 200 200" className="w-full h-full">
          <defs>
            <radialGradient id="compassGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="needleHead" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="100%" stopColor="#38bdf8" />
            </linearGradient>
            <linearGradient id="needleTail" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#94a3b8" />
              <stop offset="100%" stopColor="#cbd5e1" />
            </linearGradient>
          </defs>

          {/* Compass Background Circle */}
          <circle cx="100" cy="100" r="94" fill="url(#compassGlow)" />
          <circle
            cx="100"
            cy="100"
            r="94"
            className="stroke-slate-200 dark:stroke-slate-800"
            strokeWidth="2"
            fill="none"
          />
          <circle
            cx="100"
            cy="100"
            r="86"
            className="stroke-slate-100 dark:stroke-slate-850"
            strokeWidth="1"
            strokeDasharray="2,4"
            fill="none"
          />

          {/* Compass Tick Marks every 30 deg */}
          {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => {
            const isCardinal = deg % 90 === 0;
            const length = isCardinal ? 10 : 5;
            const rad = ((deg - 90) * Math.PI) / 180;
            const x1 = 100 + 88 * Math.cos(rad);
            const y1 = 100 + 88 * Math.sin(rad);
            const x2 = 100 + (88 - length) * Math.cos(rad);
            const y2 = 100 + (88 - length) * Math.sin(rad);

            return (
              <line
                key={deg}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                className={
                  isCardinal
                    ? 'stroke-slate-400 dark:stroke-slate-500 stroke-[2]'
                    : 'stroke-slate-300 dark:stroke-slate-700 stroke-[1]'
                }
              />
            );
          })}

          {/* Cardinal & Intercardinal Labels */}
          <text x="100" y="24" textAnchor="middle" className="text-[13px] font-extrabold fill-sky-600 dark:fill-sky-400">N</text>
          <text x="178" y="104" textAnchor="middle" className="text-[12px] font-bold fill-slate-700 dark:fill-slate-300">E</text>
          <text x="100" y="184" textAnchor="middle" className="text-[12px] font-bold fill-slate-700 dark:fill-slate-300">S</text>
          <text x="22" y="104" textAnchor="middle" className="text-[12px] font-bold fill-slate-700 dark:fill-slate-300">W</text>

          {/* Intercardinals */}
          <text x="156" y="46" textAnchor="middle" className="text-[9px] font-medium fill-slate-400 dark:fill-slate-600">NE</text>
          <text x="156" y="162" textAnchor="middle" className="text-[9px] font-medium fill-slate-400 dark:fill-slate-600">SE</text>
          <text x="44" y="162" textAnchor="middle" className="text-[9px] font-medium fill-slate-400 dark:fill-slate-600">SW</text>
          <text x="44" y="46" textAnchor="middle" className="text-[9px] font-medium fill-slate-400 dark:fill-slate-600">NW</text>

          {/* Dynamic Rotating Pointer / Needle */}
          {hasData ? (
            <g
              transform={`rotate(${normalizedDegrees} 100 100)`}
              className="transition-transform duration-700 ease-out"
            >
              {/* Origin indicator (direction wind comes from) */}
              <polygon
                points="100,28 92,95 108,95"
                fill="url(#needleHead)"
                filter="drop-shadow(0px 2px 4px rgba(2,132,199,0.35))"
              />
              {/* Destination tail (direction wind blows to) */}
              <polygon
                points="100,172 94,105 106,105"
                fill="url(#needleTail)"
              />
              {/* Central Pivot Hub */}
              <circle cx="100" cy="100" r="8" className="fill-white dark:fill-slate-900 stroke-sky-500 stroke-2" />
              <circle cx="100" cy="100" r="4" className="fill-sky-600" />
            </g>
          ) : (
            <text x="100" y="105" textAnchor="middle" className="text-xs fill-slate-400">--</text>
          )}
        </svg>
      </div>

      {/* Description readout */}
      <div className="w-full mt-2 text-center bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-xl border border-slate-100 dark:border-slate-800">
        {hasData ? (
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            <span className="font-semibold text-sky-600 dark:text-sky-400">{t('wind_flowing_from')} {currentCardinal} ({normalizedDegrees}°)</span>{' '}
            <span className="text-slate-400">&rarr;</span>{' '}
            <span>{t('wind_blowing_towards')} <strong className="text-slate-700 dark:text-slate-200">{blowingTowardsCardinal} ({blowingTowardsDegrees}°)</strong></span>
          </p>
        ) : (
          <p className="text-xs text-slate-400 italic">
            {t('wind_data_unavailable')}
          </p>
        )}
      </div>
    </div>
  );
};
