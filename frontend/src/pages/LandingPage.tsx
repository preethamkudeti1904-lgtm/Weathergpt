import React from 'react';
import { useWeather } from '../contexts/WeatherContext';
import {
  CloudSun,
  Bot,
  AlertTriangle,
  MapPin,
  BarChart3,
  Globe,
  Mic,
  Map as MapIcon,
  ArrowRight,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';

interface LandingPageProps {
  onNavigate: (page: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  const { t } = useWeather();

  const features = [
    {
      icon: CloudSun,
      title: "Real-Time Weather",
      desc: "Live surface observations covering temperature, wind velocity, humidity, pressure and precipitation."
    },
    {
      icon: Bot,
      title: "AI Weather Assistant",
      desc: "Conversational WeatherGPT grounded strictly in live meteorological observations—no hallucinations."
    },
    {
      icon: AlertTriangle,
      title: "Weather Alerts",
      desc: "Standardized IMD early warnings for heavy downpours, cyclones, thunderstorms, heatwaves and dense fog."
    },
    {
      icon: MapPin,
      title: "Location-Based Forecasts",
      desc: "Pinpoint atmospheric outlooks across districts, coastal belts and agricultural zones across India."
    },
    {
      icon: BarChart3,
      title: "Climate Insights",
      desc: "Longitudinal climate trends, rainfall distribution cycles, and climatological normals analysis."
    },
    {
      icon: Globe,
      title: "Multilingual Support",
      desc: "Native conversational intelligence in 8 Indian languages: Hindi, Telugu, Tamil, Kannada, and more."
    },
    {
      icon: Mic,
      title: "Voice Interaction",
      desc: "Natural speech-to-text queries and voice playback designed for seamless hands-free operation."
    },
    {
      icon: MapIcon,
      title: "Interactive Weather Map",
      desc: "Satellite imagery, road maps, hybrid layers with live thermal isotherms and radar overlays."
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col">
      {/* Landing Header */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-primary-600 text-white flex items-center justify-center shadow-sm">
              <CloudSun className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-slate-900 dark:text-white">
                WeatherGPT
              </span>
              <span className="ml-2 text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                IMD / MoES
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600 dark:text-slate-300">
            <a href="#features" className="hover:text-primary-600 transition">Features</a>
            <a href="#about" className="hover:text-primary-600 transition">About</a>
            <button onClick={() => onNavigate('login')} className="hover:text-primary-600 transition">
              {t('nav_login')}
            </button>
            <button
              onClick={() => onNavigate('register')}
              className="px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-xs font-semibold transition shadow-sm"
            >
              {t('nav_register')}
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex-1 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/60 border border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300 text-xs font-medium mb-6">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>India Meteorological Department SIH Platform</span>
        </div>

        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white max-w-4xl leading-tight">
          {t('hero_title')}
        </h1>

        <p className="mt-4 text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl leading-relaxed">
          {t('hero_subtitle')}
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
          <button
            onClick={() => onNavigate('dashboard')}
            className="w-full sm:w-auto px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm flex items-center justify-center gap-2 transition shadow-md"
          >
            <span>{t('btn_get_started')}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onNavigate('current')}
            className="w-full sm:w-auto px-6 py-3 rounded-lg bg-white dark:bg-slate-850 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 font-semibold text-sm transition"
          >
            {t('btn_explore')}
          </button>
        </div>

        {/* Clean Weather/Map Visual Preview */}
        <div className="mt-12 w-full max-w-4xl bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 shadow-xl">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-primary-600 font-semibold uppercase">National Station</span>
              <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">Guntur, AP</div>
              <div className="text-2xl font-extrabold text-primary-600 mt-2">31.6°C</div>
              <p className="text-xs text-slate-400 mt-1">Overcast • Humidity 72%</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-emerald-600 font-semibold uppercase">Conversational AI</span>
              <div className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-1">"Will it rain tomorrow?"</div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                "Yes, 55% rain probability with 0.8 mm light drizzle expected. Carry an umbrella."
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800">
              <span className="text-xs text-amber-600 font-semibold uppercase">Disaster Threat Grid</span>
              <div className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-1">Active Alerts: 0</div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                All coastal & inland sectors operating under normal meteorological posture.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section */}
      <section id="features" className="py-16 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
              Meteorological Intelligence for Every Sector
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
              Designed according to scientific standards for precision, accessibility and rapid response.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((f, idx) => {
              const Icon = f.icon;
              return (
                <div
                  key={idx}
                  className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 hover:border-primary-400 dark:hover:border-primary-600 transition"
                >
                  <div className="w-9 h-9 rounded-lg bg-primary-100 dark:bg-primary-950 text-primary-600 dark:text-primary-400 flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">{f.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-400">
        <p>WeatherGPT — Built for India Meteorological Department (IMD) / Ministry of Earth Sciences</p>
      </footer>
    </div>
  );
};
