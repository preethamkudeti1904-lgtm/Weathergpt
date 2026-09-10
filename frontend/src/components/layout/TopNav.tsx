import React, { useState, useEffect, useRef } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { LANGUAGES, LanguageCode } from '../../i18n/translations';
import { api } from '../../services/api';
import { LocationItem } from '../../types';
import {
  CloudSun,
  Search,
  MapPin,
  Globe,
  Sun,
  Moon,
  Bell,
  User,
  Menu,
  X,
  Check,
  LogOut,
  Sliders,
  AlertTriangle,
  Flame,
  Crosshair,
  Loader2,
  Clock
} from 'lucide-react';

interface TopNavProps {
  onOpenMobileNav: () => void;
  onOpenRoleModal: () => void;
  onNavigate: (page: string) => void;
}

export const TopNav: React.FC<TopNavProps> = ({ onOpenMobileNav, onOpenRoleModal, onNavigate }) => {
  const {
    currentLocation,
    location,
    latitude,
    longitude,
    accuracy,
    locationSource,
    gpsStatus,
    useMyLocation,
    setLocation,
    timezone,
    timezoneAbbreviation,
    localTimeStr,
    language,
    setLanguage,
    alerts,
    isDemoMode,
    toggleDemoMode,
    t
  } = useWeather();
  const { isDark, toggleTheme } = useTheme();
  const { user, logout, isAuthenticated } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LocationItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const searchRef = useRef<HTMLDivElement>(null);
  const langRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  // Debounced location search
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await api.searchLocations(searchQuery);
        setSearchResults(results);
      } catch (err) {
        console.error(err);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside listeners
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchDropdown(false);
      }
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setShowLangMenu(false);
      }
      if (userRef.current && !userRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectLocation = (loc: LocationItem) => {
    setLocation(loc.display_name, loc.latitude, loc.longitude);
    setSearchQuery('');
    setShowSearchDropdown(false);
  };

  const alertCount = alerts?.alerts?.length || 0;

  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800 transition-colors">
      {isDemoMode && (
        <div className="bg-amber-500 text-slate-950 px-4 py-1 text-xs font-semibold text-center tracking-wide flex items-center justify-center gap-2">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>DEMO DATA: Synthetic Simulation Active. Real live APIs are bypassed in demo mode.</span>
          <button onClick={toggleDemoMode} className="underline hover:text-white ml-2 text-xs">Switch to Real Data</button>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        {/* Left: Mobile Drawer Trigger & Brand */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenMobileNav}
            className="lg:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 focus:outline-none"
            aria-label="Open Navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div
            onClick={() => onNavigate('dashboard')}
            className="flex items-center gap-2.5 cursor-pointer group select-none"
          >
            <div className="w-9 h-9 rounded-lg bg-primary-600 text-white flex items-center justify-center shadow-sm">
              <CloudSun className="w-5 h-5" />
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base tracking-tight text-slate-900 dark:text-white">
                  WeatherGPT
                </span>
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                  IMD / MoES
                </span>
              </div>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-none">
                National Weather Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Center: Search Location & Live GPS Quick Action */}
        <div className="flex-1 max-w-md flex items-center gap-1.5" ref={searchRef}>
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowSearchDropdown(true);
              }}
              onFocus={() => setShowSearchDropdown(true)}
              placeholder={t('search_placeholder')}
              className="w-full pl-9 pr-8 py-1.5 text-xs sm:text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

              {/* Search Dropdown */}
            {showSearchDropdown && (searchQuery.trim().length >= 2 || searchResults.length > 0) && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-xl py-1.5 z-50 max-h-64 overflow-y-auto">
                {isSearching ? (
                  <div className="px-3 py-2 text-xs text-slate-400 text-center">{t('searching_real_locations')}</div>
                ) : searchResults.length > 0 ? (
                  searchResults.map((item, idx) => (
                    <button
                      key={`${item.latitude}-${item.longitude}-${idx}`}
                      onClick={() => handleSelectLocation(item)}
                      className="w-full text-left px-3 py-2 text-xs hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center justify-between text-slate-700 dark:text-slate-200"
                    >
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-primary-500 flex-shrink-0" />
                        <span className="font-medium">{item.display_name}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {item.latitude.toFixed(2)}°, {item.longitude.toFixed(2)}°
                      </span>
                    </button>
                  ))
                ) : (
                  <div className="px-3 py-2 text-xs text-slate-400 text-center">{t('no_locations_found')}</div>
                )}
              </div>
            )}
          </div>

          <button
            onClick={() => useMyLocation()}
            disabled={gpsStatus === 'loading'}
            className={`p-2 rounded-lg border transition flex items-center justify-center flex-shrink-0 ${
              locationSource === 'gps'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800 shadow-sm'
                : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'
            }`}
            title={t('use_my_location')}
          >
            {gpsStatus === 'loading' ? (
              <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
            ) : (
              <Crosshair className={`w-4 h-4 ${locationSource === 'gps' ? 'text-emerald-600 dark:text-emerald-400' : ''}`} />
            )}
          </button>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          {/* Current Location Pill */}
          <div
            onClick={() => onNavigate('locations')}
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 cursor-pointer transition border border-slate-200 dark:border-slate-700 max-w-[220px] truncate"
            title={`${currentLocation.name} (${currentLocation.latitude.toFixed(4)}°, ${currentLocation.longitude.toFixed(4)}°)`}
          >
            <MapPin className="w-3.5 h-3.5 text-primary-500 flex-shrink-0" />
            <span className="truncate font-medium">{currentLocation.name || location.split(',')[0]}</span>
            {currentLocation.source === 'gps' && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 flex-shrink-0">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                GPS{currentLocation.accuracy ? ` ±${Math.round(currentLocation.accuracy)}m` : ''}
              </span>
            )}
            {currentLocation.source === 'default' && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 flex-shrink-0">
                DEFAULT
              </span>
            )}
            {currentLocation.source === 'ip_approximate' && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 flex-shrink-0">
                APPROX
              </span>
            )}
          </div>

          {/* Language Selector */}
          <div className="relative" ref={langRef}>
            <button
              onClick={() => setShowLangMenu(!showLangMenu)}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1 text-xs"
              title={t('language')}
            >
              <Globe className="w-4 h-4" />
              <span className="hidden sm:inline font-medium uppercase">{language}</span>
            </button>

            {showLangMenu && (
              <div className="absolute right-0 mt-1 w-44 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-xl py-1 z-50">
                <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
                  {t('language')}
                </div>
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang.code);
                      setShowLangMenu(false);
                    }}
                    className={`w-full text-left px-3 py-1.5 text-xs flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800 ${
                      language === lang.code
                        ? 'font-semibold text-primary-600 dark:text-primary-400 bg-primary-50/50 dark:bg-primary-950/30'
                        : 'text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <span>{lang.nativeName}</span>
                    <span className="text-[10px] text-slate-400">{lang.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title={isDark ? t('theme_light') : t('theme_dark')}
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          {/* Selected Location Local Time Live Clock */}
          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold text-slate-800 dark:text-slate-100 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm select-none"
            title={`${t('current_location')} ${location.split(',')[0]} (${timezone})`}
          >
            <Clock className="w-3.5 h-3.5 text-primary-500" />
            <span className="font-mono tracking-tight text-[11px] sm:text-xs">
              {localTimeStr || '12:00 PM IST'}
            </span>
          </div>

          {/* Alerts Bell */}
          <button
            onClick={() => onNavigate('alerts')}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition relative"
            title={t('alerts')}
          >
            <Bell className="w-4 h-4" />
            {alertCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-amber-500 text-white text-[10px] font-bold flex items-center justify-center">
                {alertCount}
              </span>
            )}
          </button>

          {/* User Profile Menu */}
          <div className="relative" ref={userRef}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5"
            >
              <div className="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 flex items-center justify-center text-xs font-semibold">
                {user ? user.name[0].toUpperCase() : 'G'}
              </div>
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-1 w-56 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-xl py-1.5 z-50">
                <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800">
                  <div className="font-semibold text-xs text-slate-900 dark:text-white truncate">
                    {user ? user.name : 'Guest User'}
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                    {user ? user.email : 'Public Session'}
                  </div>
                  <div className="mt-1.5 inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800">
                    {t('user_mode_label')}: {user?.user_type || 'General User'}
                  </div>
                </div>

                <button
                  onClick={() => {
                    onOpenRoleModal();
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2"
                >
                  <Sliders className="w-3.5 h-3.5 text-slate-400" />
                  <span>{t('switch_role')}</span>
                </button>

                <button
                  onClick={() => {
                    onNavigate('settings');
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-3 py-1.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2"
                >
                  <Sliders className="w-3.5 h-3.5 text-slate-400" />
                  <span>{t('settings')}</span>
                </button>

                {isAuthenticated ? (
                  <button
                    onClick={() => {
                      logout();
                      setShowUserMenu(false);
                      onNavigate('login');
                    }}
                    className="w-full text-left px-3 py-1.5 text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 flex items-center gap-2 border-t border-slate-100 dark:border-slate-800 mt-1"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>{t('logout')}</span>
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onNavigate('login');
                    }}
                    className="w-full text-left px-3 py-1.5 text-xs text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-950/30 flex items-center gap-2 border-t border-slate-100 dark:border-slate-800 mt-1"
                  >
                    <User className="w-3.5 h-3.5" />
                    <span>{t('login')} / {t('register')}</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
