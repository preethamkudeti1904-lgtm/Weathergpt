import React, { useEffect, useState } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { api } from '../../services/api';
import { Waves, Wind, Compass, AlertTriangle, Ship } from 'lucide-react';

export const MarineWeather: React.FC = () => {
  const { location } = useWeather();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await api.getMarineWeather(location);
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [location]);

  return (
    <div className="space-y-4">
      <div className="bg-cyan-900 text-white rounded-xl p-5 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-950 flex items-center justify-center">
            <Waves className="w-5 h-5 text-cyan-300" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Marine & Coastal Weather Advisory</h2>
            <p className="text-xs text-cyan-200">Sea state, coastal winds & port warnings for maritime operations</p>
          </div>
        </div>
        <span className="px-2.5 py-1 rounded bg-cyan-950 border border-cyan-700 text-xs font-bold">
          Beaufort Force {data?.beaufort_force || 3}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><Waves className="w-4 h-4 text-cyan-500" /> Estimated Sea State</span>
          <div className="text-lg font-bold text-slate-900 dark:text-white mt-1">{data?.estimated_sea_state || 'Moderate'}</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><Wind className="w-4 h-4 text-teal-500" /> Coastal Wind Velocity</span>
          <div className="text-lg font-bold text-slate-900 dark:text-white mt-1">{data?.wind_speed_knots || 12} knots ({data?.wind_speed_kmh} km/h)</div>
          <span className="text-[10px] text-slate-400">Direction: {data?.wind_direction}</span>
        </div>
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><AlertTriangle className="w-4 h-4 text-amber-500" /> Fishermen Warning</span>
          <div className="text-sm font-bold text-slate-900 dark:text-white mt-1">{data?.fishermen_warning || 'Standard surveillance'}</div>
        </div>
      </div>
    </div>
  );
};
