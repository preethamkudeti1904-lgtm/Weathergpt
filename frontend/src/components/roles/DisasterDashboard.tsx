import React, { useEffect, useState } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { api } from '../../services/api';
import { AlertBanner } from '../weather/AlertBanner';
import {
  ShieldAlert,
  Wind,
  Droplets,
  Gauge,
  CheckSquare,
  AlertTriangle,
  Radio,
  MapPin
} from 'lucide-react';

export const DisasterDashboard: React.FC = () => {
  const { location, weather, alerts } = useWeather();
  const [disasterInfo, setDisasterInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadDisaster = async () => {
      setLoading(true);
      try {
        const data = await api.getDisasterDashboard(location);
        setDisasterInfo(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadDisaster();
  }, [location]);

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-600/90 flex items-center justify-center text-white">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold">Disaster Management Command Post</h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                {disasterInfo?.emergency_status || 'MONITORING'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Rapid assessment of extreme precipitation, convective squalls, and flood vulnerability for {location}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <Radio className="w-4 h-4 text-red-500 animate-pulse" />
          <span className="text-slate-300 font-mono">Live IMD Threat Grid</span>
        </div>
      </div>

      {/* Prominent Severe Alert Section */}
      <div className="space-y-2">
        <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          Active Threat Advisories
        </h3>
        <AlertBanner alerts={alerts?.alerts || []} />
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
            <Droplets className="w-4 h-4 text-blue-500" /> Flood / Inundation Risk
          </span>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1.5">
            {disasterInfo?.key_risk_indicators?.flood_inundation_risk || 'Normal'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            {disasterInfo?.key_risk_indicators?.heavy_rainfall_threat || 'Standard runoff'}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
            <Wind className="w-4 h-4 text-teal-500" /> Cyclonic Wind Status
          </span>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1.5">
            {disasterInfo?.key_risk_indicators?.cyclonic_wind_status || 'No Disturbance'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Current Sustained: {disasterInfo?.key_risk_indicators?.current_wind_speed || '10 km/h'}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
            <Gauge className="w-4 h-4 text-indigo-500" /> Central Pressure Tendency
          </span>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white mt-1.5">
            {weather?.pressure || 1012} hPa
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Standard atmospheric gradient
          </p>
        </div>
      </div>

      {/* Emergency Readiness Checklist */}
      <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3 flex items-center gap-2">
          <CheckSquare className="w-4 h-4 text-primary-600" />
          Standard Operating Procedure (SOP) Action Checklist
        </h4>
        <div className="space-y-2">
          {disasterInfo?.response_checklist?.map((item: string, idx: number) => (
            <div
              key={idx}
              className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300"
            >
              <input type="checkbox" className="mt-0.5 rounded text-primary-600 focus:ring-0" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
