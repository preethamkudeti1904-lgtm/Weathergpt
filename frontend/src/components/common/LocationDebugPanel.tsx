import React, { useState } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { Bug, ChevronDown, ChevronUp, MapPin } from 'lucide-react';

/**
 * Developer-only Location Diagnostic Panel (Section 25)
 * Displays active coordinates, accuracy, source, and reverse geocoding details.
 * Rendered only during local development or when ?debug=location is present.
 */
export const LocationDebugPanel: React.FC = () => {
  const { currentLocation, latitude, longitude, accuracy, locationSource } = useWeather();
  const [isExpanded, setIsExpanded] = useState(false);

  // Show only in dev mode or with ?debug query param
  const isDebugMode = 
    Boolean((import.meta as any).env?.DEV) || 
    (typeof window !== 'undefined' && window.location.search.includes('debug'));

  if (!isDebugMode) return null;

  const reverseGeocodedFull = [
    currentLocation.name,
    currentLocation.district,
    currentLocation.state,
    currentLocation.country
  ].filter(Boolean).join(', ');

  return (
    <div className="fixed bottom-3 right-3 z-50 max-w-sm w-full bg-slate-900/95 backdrop-blur text-slate-100 text-xs rounded-xl border border-slate-700 shadow-2xl p-3 font-mono">
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center gap-2">
          <Bug className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-bold tracking-wide text-slate-200">Location Diagnostics (Dev)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
            locationSource === 'gps' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-slate-800 text-slate-400'
          }`}>
            {locationSource.toUpperCase()}
          </span>
          {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronUp className="w-4 h-4 text-slate-400" />}
        </div>
      </div>

      {isExpanded && (
        <div className="mt-3 pt-2.5 border-t border-slate-800 space-y-1.5 text-[11px] leading-relaxed">
          <div className="flex justify-between">
            <span className="text-slate-400">Location Name:</span>
            <span className="text-emerald-300 font-bold">{currentLocation.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Source:</span>
            <span className="text-slate-200 font-bold">{locationSource.toUpperCase()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Latitude:</span>
            <span className="text-slate-200">{latitude.toFixed(6)}°</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Longitude:</span>
            <span className="text-slate-200">{longitude.toFixed(6)}°</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Accuracy:</span>
            <span className={accuracy && accuracy > 1000 ? 'text-amber-400 font-bold' : 'text-slate-200'}>
              {accuracy !== null ? `±${accuracy} meters` : 'N/A (Search/Default)'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Timestamp:</span>
            <span className="text-slate-400 text-[10px]">{currentLocation.timestamp}</span>
          </div>
          <div className="pt-1.5 border-t border-slate-800/80">
            <span className="text-slate-400 block text-[10px]">Reverse Geocoded:</span>
            <span className="text-slate-300 break-words">{reverseGeocodedFull}</span>
          </div>
        </div>
      )}
    </div>
  );
};
