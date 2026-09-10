import React, { useState, useEffect, useRef } from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { LANGUAGES, LanguageCode } from '../i18n/translations';
import { api } from '../services/api';
import { SmsAlertSettings, SmsDeliveryItem } from '../types';
import {
  Sun,
  Moon,
  Monitor,
  Globe,
  MapPin,
  Phone,
  ShieldCheck,
  ShieldAlert,
  Send,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Clock,
  Check,
  X,
  History
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const {
    language,
    setLanguage,
    tempUnit,
    setTempUnit,
    windUnit,
    setWindUnit,
    location,
    latitude,
    longitude,
    setLocation,
    isDemoMode,
    toggleDemoMode,
    currentLocation,
    t
  } = useWeather();
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();

  // SMS Settings State
  const [smsSettings, setSmsSettings] = useState<SmsAlertSettings | null>(null);
  const [smsHistory, setSmsHistory] = useState<SmsDeliveryItem[]>([]);
  const [isLoadingSms, setIsLoadingSms] = useState(false);
  const [isSavingSms, setIsSavingSms] = useState(false);
  const [testSmsStatus, setTestSmsStatus] = useState<string | null>(null);
  const [isSendingTest, setIsSendingTest] = useState(false);

  // Phone Change & OTP State
  const [showPhoneModal, setShowPhoneModal] = useState(false);
  const [newPhone, setNewPhone] = useState('');
  const [newCountryCode, setNewCountryCode] = useState('+91');
  const [otpStep, setOtpStep] = useState<'input_phone' | 'input_otp'>('input_phone');
  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [resendTimer, setResendTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const [phoneModalError, setPhoneModalError] = useState<string | null>(null);

  const ALL_CATEGORIES = [
    'Severe Weather',
    'Flood',
    'Cyclone',
    'Thunderstorm',
    'Extreme Rain',
    'Heatwave',
    'Cold Wave',
    'Coastal Hazard'
  ];

  const loadSmsData = async () => {
    setIsLoadingSms(true);
    try {
      const [settings, history] = await Promise.all([
        api.getSmsAlertSettings(),
        api.getSmsAlertHistory(10)
      ]);
      if (settings) {
        setSmsSettings(settings);
      }
      if (history?.deliveries) {
        setSmsHistory(history.deliveries);
      }
    } catch (err) {
      console.warn('Error fetching SMS alert settings:', err);
    } finally {
      setIsLoadingSms(false);
    }
  };

  useEffect(() => {
    loadSmsData();
  }, [user]);

  // Resend OTP countdown
  useEffect(() => {
    let interval: any = null;
    if (showPhoneModal && otpStep === 'input_otp' && resendTimer > 0) {
      interval = setInterval(() => {
        setResendTimer((prev) => {
          if (prev <= 1) {
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [showPhoneModal, otpStep, resendTimer]);

  const handleToggleSms = async () => {
    if (!smsSettings) return;
    if (!smsSettings.phone_verified && !smsSettings.sms_alerts_enabled) {
      setShowPhoneModal(true);
      return;
    }

    const nextState = !smsSettings.sms_alerts_enabled;
    setIsSavingSms(true);
    try {
      await api.updateSmsAlertSettings(nextState, smsSettings.sms_alert_categories);
      setSmsSettings({ ...smsSettings, sms_alerts_enabled: nextState });

      // Save alert location if turning on
      if (nextState && currentLocation) {
        await api.saveAlertLocation({
          latitude: currentLocation.latitude,
          longitude: currentLocation.longitude,
          location_name: currentLocation.name,
          district: currentLocation.district,
          state: currentLocation.state,
          country: currentLocation.country,
          timezone: currentLocation.timezone,
          accuracy: currentLocation.accuracy,
          source: currentLocation.source,
          label: 'Primary',
          is_primary: true,
          is_active: true
        });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update SMS disaster alert preferences.');
    } finally {
      setIsSavingSms(false);
    }
  };

  const handleCategoryToggle = async (category: string) => {
    if (!smsSettings) return;
    const current = smsSettings.sms_alert_categories || [];
    const nextCategories = current.includes(category)
      ? current.filter((c) => c !== category)
      : [...current, category];

    setSmsSettings({ ...smsSettings, sms_alert_categories: nextCategories });
    try {
      await api.updateSmsAlertSettings(smsSettings.sms_alerts_enabled, nextCategories);
    } catch (e) {
      console.warn('Failed to update categories:', e);
    }
  };

  const handleSendTestSms = async () => {
    setIsSendingTest(true);
    setTestSmsStatus(null);
    try {
      const res = await api.sendTestSms('Heavy Rain', 'Warning', true);
      setTestSmsStatus(`✓ Test SMS Sent to ${res.phone_number} (ID: ${res.message_id || 'OK'})`);
      await loadSmsData();
    } catch (err: any) {
      setTestSmsStatus(`✗ ${err.message || 'Test SMS dispatch failed'}`);
    } finally {
      setIsSendingTest(false);
    }
  };

  // Phone Change & OTP Handlers
  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhoneModalError(null);
    if (!newPhone.trim()) {
      setPhoneModalError('Please enter a valid phone number.');
      return;
    }

    const fullPhone = `${newCountryCode}${newPhone.replace(/\D/g, '')}`;
    try {
      await api.sendPhoneOtp(fullPhone, newCountryCode);
      setOtpStep('input_otp');
      setResendTimer(60);
      setCanResend(false);
      setOtpDigits(['', '', '', '', '', '']);
    } catch (err: any) {
      setPhoneModalError(err.message || 'Failed to send OTP.');
    }
  };

  const handleOtpDigitChange = (index: number, val: string) => {
    if (!/^\d*$/.test(val)) return;
    const copy = [...otpDigits];
    copy[index] = val.slice(-1);
    setOtpDigits(copy);
    if (val && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpDigits[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyNewPhone = async () => {
    const code = otpDigits.join('');
    if (code.length !== 6) {
      setPhoneModalError('Please enter the 6-digit OTP.');
      return;
    }

    const fullPhone = `${newCountryCode}${newPhone.replace(/\D/g, '')}`;
    try {
      await api.verifyPhoneOtp(fullPhone, code);
      setShowPhoneModal(false);
      setNewPhone('');
      setOtpStep('input_phone');
      await loadSmsData();
    } catch (err: any) {
      setPhoneModalError(err.message || 'Incorrect verification code.');
    }
  };

  const handleUpdateAlertLocation = async () => {
    if (!currentLocation) return;
    try {
      await api.saveAlertLocation({
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        location_name: currentLocation.name,
        district: currentLocation.district,
        state: currentLocation.state,
        country: currentLocation.country,
        timezone: currentLocation.timezone,
        accuracy: currentLocation.accuracy,
        source: currentLocation.source,
        label: 'Primary',
        is_primary: true,
        is_active: true
      });
      await loadSmsData();
      alert(`Alert location updated to ${currentLocation.name}`);
    } catch (err) {
      alert('Failed to update alert location.');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">
          {t('settings_title') || 'Settings & Preferences'}
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Manage meteorological units, language, and real-time SMS disaster notifications
        </p>
      </div>

      {/* DISASTER ALERT & SMS SETTINGS */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm divide-y divide-slate-100 dark:divide-slate-800">
        <div className="p-5 bg-gradient-to-r from-red-500/5 via-amber-500/5 to-transparent">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 font-bold text-sm text-slate-900 dark:text-white">
                <ShieldAlert className="w-4 h-4 text-red-500" />
                <span>Location-Based Disaster SMS Alerts</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300 font-bold uppercase tracking-wider">
                  SACHET / NDMA
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xl">
                Automatic official weather and emergency disaster warnings sent directly to your phone when an official warning polygon encompasses your location.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleToggleSms}
                disabled={isSavingSms || isLoadingSms}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-sm ${
                  smsSettings?.sms_alerts_enabled
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
                }`}
              >
                {smsSettings?.sms_alerts_enabled ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>SMS Alerts: ON</span>
                  </>
                ) : (
                  <>
                    <X className="w-3.5 h-3.5" />
                    <span>SMS Alerts: OFF</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Linked Phone Number & Verification */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
              <Phone className="w-4 h-4 text-primary-500" />
              <span>Registered Phone Number</span>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="font-mono text-sm font-bold text-slate-800 dark:text-slate-200">
                {smsSettings?.masked_phone || user?.phone_number || 'No phone registered'}
              </span>
              {smsSettings?.phone_verified ? (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 text-[10px] font-bold">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Verified</span>
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 text-[10px] font-bold">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Unverified</span>
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Phone number is kept private and never exposed.
            </p>
          </div>

          <button
            onClick={() => {
              setPhoneModalError(null);
              setOtpStep('input_phone');
              setShowPhoneModal(true);
            }}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition shadow-sm"
          >
            {smsSettings?.phone_verified ? 'Change Phone Number' : 'Verify Phone Number'}
          </button>
        </div>

        {/* Saved Alert Location */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
              <MapPin className="w-4 h-4 text-emerald-500" />
              <span>Monitored Alert Location</span>
            </div>
            <div className="text-sm font-bold text-slate-800 dark:text-slate-200 mt-1">
              {smsSettings?.alert_location?.name || location}
            </div>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5">
              Coordinates: {smsSettings?.alert_location?.latitude ?? latitude}°, {smsSettings?.alert_location?.longitude ?? longitude}°
            </div>
            <p className="text-[10px] text-slate-400 mt-0.5">
              Official warning polygons are evaluated geometrically against these exact coordinates.
            </p>
          </div>

          <button
            onClick={handleUpdateAlertLocation}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition shadow-sm"
          >
            Sync to Selected Location
          </button>
        </div>

        {/* Alert Categories Checkboxes */}
        <div className="p-5 space-y-3">
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Subscribed Warning Categories
            </h4>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Select which official hazard alerts should trigger an SMS message to your phone
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
            {ALL_CATEGORIES.map((cat) => {
              const isChecked = smsSettings?.sms_alert_categories?.includes(cat);
              return (
                <label
                  key={cat}
                  className={`flex items-center gap-2 p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                    isChecked
                      ? 'border-primary-500/50 bg-primary-50/50 dark:bg-primary-950/20 text-slate-900 dark:text-white font-medium'
                      : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-850'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => handleCategoryToggle(cat)}
                    className="w-3.5 h-3.5 rounded text-primary-600 focus:ring-primary-500 border-slate-300 dark:border-slate-700"
                  />
                  <span>{cat}</span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Test SMS Dispatcher */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/50 dark:bg-slate-850/50">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
              <Send className="w-4 h-4 text-blue-500" />
              <span>Simulate Official Disaster SMS</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-bold">
                TEST
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Verify end-to-end telecom transmission to your phone without waiting for an active disaster.
            </p>
            {testSmsStatus && (
              <p className="text-xs font-semibold mt-1 text-primary-600 dark:text-primary-400">
                {testSmsStatus}
              </p>
            )}
          </div>

          <button
            onClick={handleSendTestSms}
            disabled={isSendingTest || !smsSettings?.phone_verified}
            className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold text-xs transition shadow-sm flex items-center gap-1.5"
          >
            <Send className={`w-3.5 h-3.5 ${isSendingTest ? 'animate-spin' : ''}`} />
            <span>{isSendingTest ? 'Dispatching...' : 'Send Test SMS'}</span>
          </button>
        </div>
      </div>

      {/* SMS ALERT DELIVERY HISTORY */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-primary-500" />
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              SMS Alert Delivery History
            </h3>
          </div>
          <button
            onClick={loadSmsData}
            className="p-1 text-slate-400 hover:text-slate-600 transition"
            title="Refresh history"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {smsHistory.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-400 rounded-lg border border-dashed border-slate-200 dark:border-slate-800">
            No official disaster SMS messages have been dispatched to your phone yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-850 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l-lg">Time</th>
                  <th className="p-2.5">Hazard</th>
                  <th className="p-2.5">Severity</th>
                  <th className="p-2.5">Phone</th>
                  <th className="p-2.5">Carrier Status</th>
                  <th className="p-2.5 rounded-r-lg">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {smsHistory.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-850/60">
                    <td className="p-2.5 font-mono text-[11px] whitespace-nowrap text-slate-400">
                      {item.sent_at ? new Date(item.sent_at).toLocaleString() : 'Recent'}
                    </td>
                    <td className="p-2.5 font-semibold text-slate-900 dark:text-white">
                      {item.hazard_type}
                    </td>
                    <td className="p-2.5">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                        {item.severity}
                      </span>
                    </td>
                    <td className="p-2.5 font-mono text-[11px]">
                      {item.phone_number}
                    </td>
                    <td className="p-2.5">
                      <span className={`inline-flex items-center gap-1 text-[11px] font-bold ${
                        item.status === 'SENT' || item.status === 'DELIVERED'
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-red-500'
                      }`}>
                        {item.status === 'SENT' || item.status === 'DELIVERED' ? '✓' : '✗'} {item.status}
                      </span>
                    </td>
                    <td className="p-2.5 text-[11px] text-slate-500 line-clamp-1 max-w-xs">
                      {item.message}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Standard Preferences: Theme, Units, Language */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 divide-y divide-slate-100 dark:divide-slate-800 shadow-sm">
        {/* Appearance */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900 dark:text-white">
              <Sun className="w-4 h-4 text-amber-500" />
              <span>{t('appearance')}</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {t('theme_light')} / {t('theme_dark')} / {t('theme_system')}
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setTheme('light')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition ${
                theme === 'light'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              <Sun className="w-3.5 h-3.5" /> {t('theme_light')}
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition ${
                theme === 'dark'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              <Moon className="w-3.5 h-3.5" /> {t('theme_dark')}
            </button>
            <button
              onClick={() => setTheme('system')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition ${
                theme === 'system'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              <Monitor className="w-3.5 h-3.5" /> {t('theme_system')}
            </button>
          </div>
        </div>

        {/* Language */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900 dark:text-white">
              <Globe className="w-4 h-4 text-blue-500" />
              <span>{t('language')}</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {t('select_language')}
            </p>
          </div>

          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as LanguageCode)}
            className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none"
          >
            {LANGUAGES.map((l: any) => (
              <option key={l.code} value={l.code}>
                {l.nativeName} ({l.name})
              </option>
            ))}
          </select>
        </div>

        {/* Temperature Unit */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900 dark:text-white">
              <span className="font-bold text-primary-500">°C/°F</span>
              <span>{t('temp_unit')}</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {t('celsius')} / {t('fahrenheit')}
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setTempUnit('celsius')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                tempUnit === 'celsius'
                  ? 'bg-white dark:bg-slate-900 text-primary-600 dark:text-primary-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              °C
            </button>
            <button
              onClick={() => setTempUnit('fahrenheit')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                tempUnit === 'fahrenheit'
                  ? 'bg-white dark:bg-slate-900 text-primary-600 dark:text-primary-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              °F
            </button>
          </div>
        </div>

        {/* Wind Speed Unit */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900 dark:text-white">
              <span className="font-bold text-teal-500">km/h</span>
              <span>{t('wind_unit')}</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {t('kmh')} / {t('ms')}
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setWindUnit('kmh')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                windUnit === 'kmh'
                  ? 'bg-white dark:bg-slate-900 text-primary-600 dark:text-primary-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              km/h
            </button>
            <button
              onClick={() => setWindUnit('ms')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                windUnit === 'ms'
                  ? 'bg-white dark:bg-slate-900 text-primary-600 dark:text-primary-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              m/s
            </button>
          </div>
        </div>

        {/* Controlled Demo Mode */}
        <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900 dark:text-white">
              <span className="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-bold">
                DEV
              </span>
              <span>Controlled Demo Mode</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Toggle synthetic development testing data. Clearly marked as DEMO DATA.
            </p>
          </div>

          <button
            onClick={toggleDemoMode}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition ${
              isDemoMode
                ? 'bg-amber-500 text-slate-950'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
            }`}
          >
            {isDemoMode ? 'DEMO MODE ACTIVE' : 'REAL DATA ACTIVE'}
          </button>
        </div>
      </div>

      {/* PHONE VERIFICATION MODAL */}
      {showPhoneModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Phone className="w-4 h-4 text-primary-500" />
                <span>{otpStep === 'input_phone' ? 'Update Phone Number' : 'Enter Verification Code'}</span>
              </h3>
              <button
                onClick={() => setShowPhoneModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {phoneModalError && (
              <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 rounded-lg text-xs text-red-700 dark:text-red-300">
                {phoneModalError}
              </div>
            )}

            {otpStep === 'input_phone' ? (
              <form onSubmit={handleRequestOtp} className="space-y-4">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Changing your phone number requires verifying the new number via a 6-digit OTP code before disaster SMS alerts can be delivered.
                </p>
                <div className="flex gap-2">
                  <select
                    value={newCountryCode}
                    onChange={(e) => setNewCountryCode(e.target.value)}
                    className="w-24 px-2 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono"
                  >
                    <option value="+91">🇮🇳 +91</option>
                    <option value="+1">🇺🇸 +1</option>
                    <option value="+44">🇬🇧 +44</option>
                    <option value="+971">🇦🇪 +971</option>
                    <option value="+65">🇸🇬 +65</option>
                  </select>
                  <input
                    type="tel"
                    required
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    placeholder="98765 43210"
                    className="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-mono"
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowPhoneModal(false)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-semibold text-xs transition"
                  >
                    Send Verification Code
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Enter the 6-digit verification code transmitted to <strong className="font-mono">{newCountryCode} {newPhone}</strong>:
                </p>
                <div className="flex justify-center gap-2">
                  {otpDigits.map((digit, idx) => (
                    <input
                      key={idx}
                      ref={(el) => (otpRefs.current[idx] = el)}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpDigitChange(idx, e.target.value)}
                      onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                      className="w-9 h-12 text-center text-lg font-black font-mono rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                    />
                  ))}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Resend code in: {resendTimer}s</span>
                  <button
                    type="button"
                    onClick={async () => {
                      if (!canResend) return;
                      const fullPhone = `${newCountryCode}${newPhone.replace(/\D/g, '')}`;
                      await api.sendPhoneOtp(fullPhone, newCountryCode);
                      setResendTimer(60);
                      setCanResend(false);
                    }}
                    disabled={!canResend}
                    className={`font-semibold ${canResend ? 'text-primary-600 hover:underline' : 'text-slate-400 cursor-not-allowed'}`}
                  >
                    Resend Code
                  </button>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setOtpStep('input_phone')}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    onClick={handleVerifyNewPhone}
                    className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition"
                  >
                    Verify & Save Phone
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
