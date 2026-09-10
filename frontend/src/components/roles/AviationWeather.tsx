import React, { useEffect, useState } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { api } from '../../services/api';
import { Plane, Eye, Wind, Thermometer, Gauge, CheckCircle2 } from 'lucide-react';

export const AviationWeather: React.FC = () => {
  const { location } = useWeather();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await api.getAviationWeather(location);
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
      <div className="bg-sky-800 text-white rounded-xl p-5 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-sky-900 flex items-center justify-center">
            <Plane className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Aviation Meteorology (MET Terminal)</h2>
            <p className="text-xs text-sky-200">Terminal weather observations & flight category for {location}</p>
          </div>
        </div>
        <span className="px-2.5 py-1 rounded bg-sky-900 border border-sky-700 text-xs font-bold uppercase">
          {data?.flight_category || 'VFR'}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><Eye className="w-3.5 h-3.5 text-blue-500" /> Surface Visibility</span>
          <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">{data?.visibility_km || 10} km</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><Wind className="w-3.5 h-3.5 text-teal-500" /> Surface Wind</span>
          <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">{data?.surface_wind?.speed_kmh || 0} km/h</div>
          <span className="text-[10px] text-slate-400">Dir: {data?.surface_wind?.direction_cardinal} ({data?.surface_wind?.direction_degrees}°)</span>
        </div>
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><Gauge className="w-3.5 h-3.5 text-indigo-500" /> Altimeter (QNH)</span>
          <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">{data?.altimeter_setting_hpa || 1013} hPa</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-400 flex items-center gap-1.5"><Thermometer className="w-3.5 h-3.5 text-amber-500" /> Temp / Dewpoint Spread</span>
          <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">{data?.temperature_c || 25}°C</div>
          <span className="text-[10px] text-slate-400">Spread: {data?.dewpoint_spread_approx_c || 5}°C</span>
        </div>
      </div>
    </div>
  );
};
