import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useWeather } from '../contexts/WeatherContext';
import { UserType } from '../types';
import { CloudSun, ArrowRight, AlertCircle, Phone, CheckCircle2, ShieldAlert, RefreshCw } from 'lucide-react';
import { LANGUAGES } from '../i18n/translations';
import { api } from '../services/api';

interface RegisterPageProps {
  onNavigate: (page: string) => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onNavigate }) => {
  const { register } = useAuth();
  const { currentLocation } = useWeather();

  const [step, setStep] = useState<'register' | 'verify_otp' | 'sms_consent'>('register');

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_country_code: '+91',
    phone_number: '',
    password: '',
    confirm_password: '',
    country: 'India',
    state: 'Andhra Pradesh',
    preferred_language: 'en',
    user_type: 'General User' as UserType,
  });

  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const otpInputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [resendTimer, setResendTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Timer countdown for OTP resend
  useEffect(() => {
    let interval: any = null;
    if (step === 'verify_otp' && resendTimer > 0) {
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
  }, [step, resendTimer]);

  const pwByteLength = new TextEncoder().encode(formData.password).length;

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Development logging: reports ONLY byte length, never password
    if ((import.meta as any)?.env?.DEV) {
      console.log('[PasswordRegistration] Password UTF-8 byte length:', pwByteLength);
    }

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match.');
      return;
    }

    if (pwByteLength > 72) {
      setError('Password is too long. Please use a shorter password.');
      return;
    }

    if (!formData.phone_number.trim()) {
      setError('Phone number is required for official disaster warning delivery.');
      return;
    }

    setIsSubmitting(true);
    try {
      // Exclude confirm_password from registration request payload
      const { confirm_password, ...registrationPayload } = formData;
      await register({
        ...registrationPayload,
        phone_number: `${formData.phone_country_code}${formData.phone_number.replace(/\D/g, '')}`
      });

      setInfoMessage(`A 6-digit verification code was sent to ${formData.phone_country_code} ${formData.phone_number}`);
      setStep('verify_otp');
      setResendTimer(60);
      setCanResend(false);
    } catch (err: any) {
      const msg = err.message || '';
      if (msg.toLowerCase().includes('72 bytes') || msg.toLowerCase().includes('too long') || msg.toLowerCase().includes('longer than 72')) {
        setError('Password is too long. Please choose a shorter password.');
      } else {
        setError(msg || 'Unable to create your account right now. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const newDigits = [...otpDigits];
    newDigits[index] = value.slice(-1);
    setOtpDigits(newDigits);

    if (value && index < 5) {
      otpInputRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpDigits[index] && index > 0) {
      otpInputRefs.current[index - 1]?.focus();
    }
  };

  const handleOtpPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (!pastedData) return;
    const newDigits = [...otpDigits];
    for (let i = 0; i < pastedData.length; i++) {
      newDigits[i] = pastedData[i];
    }
    setOtpDigits(newDigits);
    const focusIndex = Math.min(pastedData.length, 5);
    otpInputRefs.current[focusIndex]?.focus();
  };

  const handleVerifyOtp = async () => {
    const fullOtp = otpDigits.join('');
    if (fullOtp.length !== 6) {
      setError('Please enter all 6 digits of the OTP.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const fullPhone = `${formData.phone_country_code}${formData.phone_number.replace(/\D/g, '')}`;
      await api.verifyPhoneOtp(fullPhone, fullOtp);
      setStep('sms_consent');
    } catch (err: any) {
      setError(err.message || 'Verification failed. Incorrect or expired code.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResendOtp = async () => {
    if (!canResend) return;
    setError(null);
    setInfoMessage(null);
    setIsSubmitting(true);
    try {
      const fullPhone = `${formData.phone_country_code}${formData.phone_number.replace(/\D/g, '')}`;
      const res = await api.sendPhoneOtp(fullPhone, formData.phone_country_code);
      setInfoMessage('New OTP code transmitted to your mobile number.');
      setResendTimer(60);
      setCanResend(false);
      setOtpDigits(['', '', '', '', '', '']);
      if (res?.dev_otp) {
        console.log(`[Dev OTP] Your test code is: ${res.dev_otp}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to resend OTP.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEnableSmsAlerts = async () => {
    setIsSubmitting(true);
    try {
      // 1. Enable SMS Alerts in preferences
      await api.updateSmsAlertSettings(true);

      // 2. Save current consented alert location
      if (currentLocation) {
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

      onNavigate('dashboard');
    } catch (e) {
      onNavigate('dashboard');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkipSmsAlerts = () => {
    onNavigate('dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4">
      <div className="max-w-lg w-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-xl">
        {/* Brand */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary-600 text-white mb-2 shadow-sm">
            <CloudSun className="w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">
            {step === 'register' && 'Create WeatherGPT Account'}
            {step === 'verify_otp' && 'Verify Your Phone Number'}
            {step === 'sms_consent' && 'Disaster SMS Alert Setup'}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {step === 'register' && 'Personalized meteorological forecasts & SMS disaster alerts'}
            {step === 'verify_otp' && `Enter the 6-digit code transmitted to ${formData.phone_country_code} ${formData.phone_number}`}
            {step === 'sms_consent' && 'Official early warnings directly to your mobile phone'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {infoMessage && (
          <div className="mb-4 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-900 text-xs text-blue-700 dark:text-blue-300 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-blue-500" />
            <span>{infoMessage}</span>
          </div>
        )}

        {/* STEP 1: REGISTRATION FORM */}
        {step === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-primary-500"
                placeholder="e.g. Ramesh Kumar"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Email Address *
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-primary-500"
                placeholder="name@example.com"
              />
            </div>

            {/* Phone Number Field */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center justify-between">
                <span>Phone Number (for Disaster SMS) *</span>
                <span className="text-[10px] text-primary-600 font-normal">OTP Verified</span>
              </label>
              <div className="flex gap-2">
                <select
                  value={formData.phone_country_code}
                  onChange={(e) => setFormData({ ...formData, phone_country_code: e.target.value })}
                  className="w-24 px-2 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none font-mono"
                >
                  <option value="+91">🇮🇳 +91</option>
                  <option value="+1">🇺🇸 +1</option>
                  <option value="+44">🇬🇧 +44</option>
                  <option value="+971">🇦🇪 +971</option>
                  <option value="+65">🇸🇬 +65</option>
                  <option value="+81">🇯🇵 +81</option>
                </select>
                <div className="relative flex-1">
                  <Phone className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="tel"
                    required
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    className="w-full pl-8 pr-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-primary-500 font-mono"
                    placeholder="98765 43210"
                  />
                </div>
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Used exclusively for sending location-based life-safety disaster warnings.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Password *
                </label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-primary-500"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Confirm Password *
                </label>
                <input
                  type="password"
                  required
                  value={formData.confirm_password}
                  onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-primary-500"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Inline Password Feedback */}
            {pwByteLength > 72 && (
              <p className="text-[11px] text-red-600 dark:text-red-400 font-medium">
                Password is too long. Please use a shorter password.
              </p>
            )}
            {formData.confirm_password && formData.password !== formData.confirm_password && (
              <p className="text-[11px] text-red-600 dark:text-red-400 font-medium">
                Passwords do not match.
              </p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Country
                </label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  State / Province
                </label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Preferred Language
                </label>
                <select
                  value={formData.preferred_language}
                  onChange={(e) => setFormData({ ...formData, preferred_language: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none"
                >
                  {LANGUAGES.map((l: any) => (
                    <option key={l.code} value={l.code}>
                      {l.nativeName} ({l.name})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  User Type / Role *
                </label>
                <select
                  value={formData.user_type}
                  onChange={(e) => setFormData({ ...formData, user_type: e.target.value as UserType })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none"
                >
                  <option value="General User">General User</option>
                  <option value="Farmer">Farmer</option>
                  <option value="Researcher">Researcher</option>
                  <option value="Disaster Management">Disaster Management</option>
                  <option value="Government / Official">Government / Official</option>
                  <option value="Aviation">Aviation</option>
                  <option value="Marine">Marine</option>
                  <option value="Student">Student</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2.5 px-4 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-semibold text-xs transition shadow-sm flex items-center justify-center gap-2 mt-4"
            >
              <span>{isSubmitting ? 'Verifying...' : 'Continue to Phone Verification'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        {/* STEP 2: PHONE OTP VERIFICATION */}
        {step === 'verify_otp' && (
          <div className="space-y-5">
            <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-center">
              <Phone className="w-8 h-8 text-primary-500 mx-auto mb-2" />
              <div className="text-xs font-bold text-slate-800 dark:text-slate-200">
                Verification Code Sent
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                Enter the 6-digit code sent to <strong className="font-mono">{formData.phone_country_code} {formData.phone_number}</strong>
              </p>
            </div>

            {/* 6-digit individual input boxes */}
            <div className="flex justify-center gap-2 sm:gap-3 my-4">
              {otpDigits.map((digit, idx) => (
                <input
                  key={idx}
                  ref={(el) => (otpInputRefs.current[idx] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(idx, e.target.value)}
                  onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                  onPaste={idx === 0 ? handleOtpPaste : undefined}
                  className="w-10 h-12 sm:w-12 sm:h-14 text-center text-lg font-black font-mono rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition shadow-sm"
                />
              ))}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Didn't receive the SMS?</span>
              <button
                type="button"
                onClick={handleResendOtp}
                disabled={!canResend || isSubmitting}
                className={`font-semibold transition flex items-center gap-1 ${
                  canResend
                    ? 'text-primary-600 dark:text-primary-400 hover:underline'
                    : 'text-slate-400 cursor-not-allowed'
                }`}
              >
                <RefreshCw className={`w-3 h-3 ${isSubmitting ? 'animate-spin' : ''}`} />
                {canResend ? 'Resend OTP' : `Resend in ${resendTimer}s`}
              </button>
            </div>

            <button
              onClick={handleVerifyOtp}
              disabled={isSubmitting || otpDigits.join('').length !== 6}
              className="w-full py-2.5 px-4 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white font-semibold text-xs transition shadow-sm flex items-center justify-center gap-2"
            >
              <span>{isSubmitting ? 'Verifying OTP...' : 'Verify Phone Number'}</span>
              <CheckCircle2 className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* STEP 3: DISASTER SMS CONSENT */}
        {step === 'sms_consent' && (
          <div className="space-y-5">
            <div className="p-5 bg-amber-50/70 dark:bg-amber-950/30 rounded-2xl border border-amber-200 dark:border-amber-900/50 text-center">
              <ShieldAlert className="w-10 h-10 text-amber-600 dark:text-amber-400 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Location-Based Disaster SMS Alerts
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                WeatherGPT can automatically send SMS notifications when an official weather or disaster warning affects your selected location.
              </p>
              <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 text-[11px] font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Phone Verified: {formData.phone_country_code} {formData.phone_number}</span>
              </div>
            </div>

            <div className="space-y-2">
              <button
                onClick={handleEnableSmsAlerts}
                disabled={isSubmitting}
                className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition shadow-sm flex items-center justify-center gap-2"
              >
                <span>{isSubmitting ? 'Activating...' : 'Enable Location-Based Disaster SMS'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={handleSkipSmsAlerts}
                disabled={isSubmitting}
                className="w-full py-2.5 px-4 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-xs transition"
              >
                Skip / Configure Later in Settings
              </button>
            </div>
          </div>
        )}

        <div className="mt-6 text-center text-xs text-slate-500">
          Already have an account?{' '}
          <button
            onClick={() => onNavigate('login')}
            className="text-primary-600 dark:text-primary-400 font-semibold hover:underline"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};
