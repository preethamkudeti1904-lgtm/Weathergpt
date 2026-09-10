import React, { useState } from 'react';
import { useWeather } from '../contexts/WeatherContext';
import { AlertBanner } from '../components/weather/AlertBanner';
import {
  AlertTriangle,
  ShieldCheck,
  Shield,
  RefreshCw,
  Clock,
  Radio,
  Waves,
  Zap,
  Flame,
  Wind,
  CloudRain,
  Eye,
  CheckCircle2,
  ChevronRight,
  Info
} from 'lucide-react';

const NDMA_DOS_DONTS: Record<string, { title: string; dos: string[]; donts: string[] }> = {
  flood: {
    title: "Flood Safety (NDMA)",
    dos: [
      "Move immediately to elevated ground or designated community flood shelters if evacuation is ordered.",
      "Keep emergency survival kits ready with potable water, battery torches, non-perishable food, and essential medicines.",
      "Listen to official broadcasts on battery-powered radios or NDMA / SACHET alerts.",
      "Boil or chlorinate drinking water before consumption to prevent waterborne contagion."
    ],
    donts: [
      "Do NOT walk, swim, or drive through moving floodwaters. (6 inches of moving water can knock down an adult; 2 feet can sweep away a car).",
      "Do NOT enter flooded basements or touch submerged electrical appliances.",
      "Do NOT ignore local authority evacuation notices."
    ]
  },
  thunderstorm: {
    title: "Thunderstorm & Lightning (NDMA)",
    dos: [
      "Seek substantial indoor shelter immediately upon hearing thunder or sighting lightning.",
      "Adhere to the 30-30 rule: If thunder is heard within 30 seconds of lightning flash, remain indoors for 30 minutes after last thunderclap.",
      "Unplug computers, televisions, and air conditioners to prevent destructive electrical surges."
    ],
    donts: [
      "Do NOT take shelter beneath isolated, tall trees or near wire fences and metallic towers.",
      "Do NOT operate tractors or hold metal umbrellas/tools in open fields.",
      "Do NOT swim or stand near water bodies during an active thunderstorm."
    ]
  },
  heatwave: {
    title: "Heat Wave & Sunstroke (NDMA)",
    dos: [
      "Drink adequate water, buttermilk, lemon water, and ORS at regular intervals, even if not thirsty.",
      "Wear loose, lightweight, light-colored cotton garments and cover your head with a hat or umbrella.",
      "Reschedule strenuous outdoor farming or construction labor to early morning or late evening."
    ],
    donts: [
      "Do NOT leave children, the elderly, or pets inside parked motor vehicles.",
      "Do NOT consume alcohol, aerated sugary soft drinks, or excessive caffeine, which dehydrate the body.",
      "Do NOT venture out unnecessarily between 12:00 PM and 4:00 PM."
    ]
  },
  cyclone: {
    title: "Cyclone & Severe Storm (NDMA)",
    dos: [
      "Secure loose rooftop objects, tin sheets, and trim weak overhanging tree branches.",
      "Move swiftly to reinforced cyclone shelters if residing in vulnerable low-lying coastal kutcha settlements.",
      "Keep sufficient battery supplies, charged mobile devices, and dry rations stored safely."
    ],
    donts: [
      "Do NOT venture into the open sea or open waters under any circumstances.",
      "Do NOT step outside during the calm 'eye of the cyclone'; winds will violently reverse in opposite direction within minutes.",
      "Do NOT touch dangling power lines or step in puddles near fallen electrical transformers."
    ]
  },
  earthquake: {
    title: "Earthquake Emergency (NDMA)",
    dos: [
      "Drop, Cover, and Hold On beneath sturdy wooden furniture or against an interior wall.",
      "Protect your head and neck with your arms and cushions.",
      "Use stairwells rather than elevators when exiting multi-story buildings after shaking halts."
    ],
    donts: [
      "Do NOT rush outside through crowded exits during active tremors where falling glass and masonry pose deadly hazards.",
      "Do NOT light matches, candles, or electrical switches until gas pipes are verified leak-free."
    ]
  }
};

export const AlertsPage: React.FC = () => {
  const { alerts, location, refreshWeather, t } = useWeather();
  const [selectedHazardTab, setSelectedHazardTab] = useState<'flood' | 'thunderstorm' | 'heatwave' | 'cyclone' | 'earthquake'>('flood');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const directList = alerts?.direct_alerts || alerts?.alerts || [];
  const regionalList = alerts?.regional_alerts || [];
  const aiRisk = alerts?.ai_risk_assessment;
  const serviceStatus = alerts?.service_status || 'operational';

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refreshWeather();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
              {t('threat_surveillance')}
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300">
              NDMA / SACHET
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time disaster warning intelligence, CAP alerts & early hazard surveillance for <strong>{location}</strong>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-primary-500 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{t('refresh_alerts') || 'Refresh Alerts'}</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {t('official_warning') || 'Official Warnings'}
          </div>
          <div className="text-2xl font-black mt-1 text-slate-900 dark:text-white flex items-baseline gap-1.5">
            <span className={directList.length > 0 ? 'text-red-600 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'}>
              {directList.length}
            </span>
            <span className="text-xs font-normal text-slate-400">active</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1">
            Directly affecting {location.split(',')[0]}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {t('regional_alerts') || 'Regional Warnings'}
          </div>
          <div className="text-2xl font-black mt-1 text-amber-600 dark:text-amber-400 flex items-baseline gap-1.5">
            {regionalList.length}
            <span className="text-xs font-normal text-slate-400">within 150 km</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1">
            Neighboring districts & zones
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {t('risk_score') || 'AI Risk Level'}
          </div>
          <div className="text-2xl font-black mt-1 text-primary-600 dark:text-primary-400 flex items-baseline gap-1.5">
            {aiRisk?.level || 'LOW'}
            <span className="text-xs font-normal text-slate-400">({aiRisk?.score || 0}/100)</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1">
            Confidence: {aiRisk?.confidence || 'Moderate'}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Feed Provider Status
          </div>
          <div className="text-sm font-bold mt-2 text-slate-900 dark:text-white flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${serviceStatus === 'operational' ? 'bg-emerald-500' : serviceStatus === 'no_alerts_found' ? 'bg-blue-500' : 'bg-amber-500'} animate-pulse`} />
            <span className="capitalize">{serviceStatus.replace(/_/g, ' ')}</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 line-clamp-1">
            {alerts?.source || 'SACHET / NDMA / IMD'}
          </p>
        </div>
      </div>

      {/* Main Threat Surveillance Component */}
      <AlertBanner alertsData={alerts} onRefresh={handleRefresh} />

      {/* Alert Timeline */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
        <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2 mb-3">
          <Clock className="w-3.5 h-3.5 text-primary-500" />
          {t('timeline') || 'Hazard Projection Timeline'}
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-7 gap-2 text-center text-xs">
          {[
            { label: 'NOW', status: directList.length > 0 ? 'Warning' : 'Normal', color: directList.length > 0 ? 'bg-red-100 text-red-700 border-red-200' : 'bg-slate-50 text-slate-600' },
            { label: '+3 Hours', status: (aiRisk?.score || 0) >= 60 ? 'Elevated' : 'Normal', color: (aiRisk?.score || 0) >= 60 ? 'bg-orange-100 text-orange-700 border-orange-200' : 'bg-slate-50 text-slate-600' },
            { label: '+6 Hours', status: (aiRisk?.score || 0) >= 50 ? 'Moderate' : 'Normal', color: (aiRisk?.score || 0) >= 50 ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-slate-50 text-slate-600' },
            { label: '+12 Hours', status: 'Monitoring', color: 'bg-slate-50 text-slate-600' },
            { label: '+24 Hours', status: 'Forecast', color: 'bg-slate-50 text-slate-600' },
            { label: '+48 Hours', status: 'Outlook', color: 'bg-slate-50 text-slate-600' },
            { label: '+7 Days', status: 'Seasonal', color: 'bg-slate-50 text-slate-600' },
          ].map((slot, i) => (
            <div key={i} className={`p-2.5 rounded-lg border border-slate-100 dark:border-slate-800 ${slot.color}`}>
              <div className="font-bold text-[11px]">{slot.label}</div>
              <div className="text-[10px] mt-0.5 font-medium">{slot.status}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive NDMA Dos & Don'ts Knowledge Base */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-500" />
              {t('safety_precautions') || 'Authoritative Safety Guidelines'} (National Disaster Management Authority)
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Verified life-safety protocols sourced directly from SACHET NDMA Disaster Guidelines
            </p>
          </div>
        </div>

        {/* Hazard Category Tabs */}
        <div className="flex flex-wrap gap-1.5 border-b border-slate-100 dark:border-slate-800 pb-2">
          {[
            { id: 'flood', label: 'Flood / Inundation', icon: Waves },
            { id: 'thunderstorm', label: 'Thunderstorm & Lightning', icon: Zap },
            { id: 'heatwave', label: 'Heat Wave', icon: Flame },
            { id: 'cyclone', label: 'Cyclone & Wind', icon: Wind },
            { id: 'earthquake', label: 'Earthquake', icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = selectedHazardTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedHazardTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  active
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Selected Guidance Content */}
        {NDMA_DOS_DONTS[selectedHazardTab] && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div className="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/50 dark:border-emerald-900/30">
              <h4 className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider flex items-center gap-1.5 mb-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                DOs (What You Should Do)
              </h4>
              <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                {NDMA_DOS_DONTS[selectedHazardTab].dos.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                    <span className="leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-red-50/50 dark:bg-red-950/20 border border-red-200/50 dark:border-red-900/30">
              <h4 className="text-xs font-bold text-red-800 dark:text-red-300 uppercase tracking-wider flex items-center gap-1.5 mb-2.5">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                DON'Ts (What to Avoid)
              </h4>
              <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                {NDMA_DOS_DONTS[selectedHazardTab].donts.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 flex-shrink-0" />
                    <span className="leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
