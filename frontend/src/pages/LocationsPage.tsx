import React, { useState, useEffect } from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { api } from '../services/api';
import { LocationItem } from '../types';
import { MapPin, Search, Trash2, Check, Plus, Star } from 'lucide-react';

export const LocationsPage: React.FC = () => {
  const { location, setLocation, t } = useWeather();
  const [savedLocations, setSavedLocations] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LocationItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    loadSaved();
  }, []);

  const loadSaved = async () => {
    const list = await api.getSavedLocations();
    setSavedLocations(list);
  };

  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await api.searchLocations(searchQuery);
        setSearchResults(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsSearching(false);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleSelect = (locName: string, lat: number, lon: number) => {
    setLocation(locName, lat, lon);
  };

  const handleSave = async (item: LocationItem) => {
    try {
      await api.saveLocation({
        location_name: item.name,
        state: item.state,
        country: item.country,
        latitude: item.latitude,
        longitude: item.longitude,
      });
      loadSaved();
      setSearchQuery('');
      setSearchResults([]);
    } catch (err) {
      // If not logged in, add to local state
      setSavedLocations(prev => [
        ...prev,
        {
          id: Date.now(),
          location_name: item.name,
          state: item.state,
          latitude: item.latitude,
          longitude: item.longitude,
        }
      ]);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">
          {t('locations')}
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          {t('station_search')} ({location})
        </p>
      </div>

      {/* Search & Add */}
      <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
          {t('search_city')}
        </h3>
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('search_placeholder')}
            className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-primary-500"
          />
        </div>

        {/* Results List */}
        {searchResults.length > 0 && (
          <div className="divide-y divide-slate-100 dark:divide-slate-800 border border-slate-100 dark:border-slate-800 rounded-lg overflow-hidden">
            {searchResults.map((item, idx) => (
              <div
                key={idx}
                className="p-3 hover:bg-slate-50 dark:hover:bg-slate-850 flex items-center justify-between text-xs transition"
              >
                <div>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{item.display_name}</span>
                  <span className="text-slate-400 ml-2 font-mono">
                    ({item.latitude.toFixed(2)}°, {item.longitude.toFixed(2)}°)
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSelect(item.display_name, item.latitude, item.longitude)}
                    className="px-2.5 py-1 rounded bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-300 hover:bg-primary-100 text-xs font-medium"
                  >
                    Select
                  </button>
                  <button
                    onClick={() => handleSave(item)}
                    className="p-1 rounded text-slate-400 hover:text-amber-500"
                    title="Bookmark Location"
                  >
                    <Star className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Saved Locations List */}
      <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
          Saved & Preset Locations
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {savedLocations.map((loc) => {
            const isSelected = location.toLowerCase().includes(loc.location_name.toLowerCase());
            return (
              <div
                key={loc.id}
                onClick={() => handleSelect(`${loc.location_name}, ${loc.state || 'India'}`, loc.latitude, loc.longitude)}
                className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-950/40'
                    : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${isSelected ? 'bg-primary-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500'}`}>
                    <MapPin className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                      {loc.location_name}
                    </h4>
                    <p className="text-xs text-slate-400">{loc.state || 'India'}</p>
                  </div>
                </div>

                {isSelected ? (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                    Active
                  </span>
                ) : (
                  <span className="text-xs text-slate-400 hover:text-primary-600">Switch →</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
