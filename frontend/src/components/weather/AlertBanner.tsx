import React, { useState } from 'react';
import { WeatherAlert, AlertsData } from '../../types';
import { useWeather } from '../../contexts/WeatherContext';
import {
  AlertTriangle,
  Clock,
  Flame,
  Wind,
  CloudRain,
  Eye,
  Zap,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Shield,
  Radio,
  RefreshCw,
  Info,
  MapPin,
  Waves
} from 'lucide-react';

interface AlertBannerProps {
  alerts?: WeatherAlert[] | null;
  alertsData?: AlertsData | null;
  onRefresh?: () => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ alerts, alertsData, onRefresh }) => {
  const { t, alerts: contextAlertsData } = useWeather();
  const [expandedAlertId, setExpandedAlertId] = useState<string | null>(null);

  // Consolidate data
  const data: AlertsData | null = alertsData || contextAlertsData;
  const directList: WeatherAlert[] = data?.direct_alerts && data.direct_alerts.length > 0
    ? data.direct_alerts
    : (Array.isArray(alerts) ? alerts : (data?.alerts || []));

  const regionalList: WeatherAlert[] = data?.regional_alerts || [];
  const aiRisk = data?.ai_risk_assessment;
  const serviceStatus = data?.service_status || 'operational';
  const serviceMessage = data?.service_message;

  const toggleExpand = (id: string) => {
    setExpandedAlertId(prev => prev === id ? null : id);
  };

  const getAlertIcon = (category: string) => {
    const c = category.toLowerCase();
    if (c.includes('rain') || c.includes('precipitation')) return <CloudRain className="w-4 h-4 text-blue-500" />;
    if (c.includes('heat') || c.includes('hot')) return <Flame className="w-4 h-4 text-red-500" />;
    if (c.includes('thunder') || c.includes('lightning') || c.includes('shower')) return <Zap className="w-4 h-4 text-amber-500" />;
    if (c.includes('wind') || c.includes('cyclone') || c.includes('squall')) return <Wind className="w-4 h-4 text-purple-500" />;
    if (c.includes('fog') || c.includes('visibility')) return <Eye className="w-4 h-4 text-slate-400" />;
    if (c.includes('flood') || c.includes('tsunami') || c.includes('wave')) return <Waves className="w-4 h-4 text-cyan-500" />;
    return <AlertTriangle className="w-4 h-4 text-amber-500" />;
  };

  const getSeverityBadge = (severity: string, colorCode: string) => {
    let bg = 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-950/40 dark:text-yellow-300 dark:border-yellow-900';
    let dot = 'bg-yellow-500';

    const s = severity.toLowerCase();
    const c = colorCode.toLowerCase();

    if (s.includes('emergency') || c === 'red') {
      bg = 'bg-red-100 text-red-800 border-red-300 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900';
      dot = 'bg-red-500';
    } else if (s.includes('warning') || c === 'orange') {
      bg = 'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900';
      dot = 'bg-orange-500';
    } else if (s.includes('information') || c === 'green') {
      bg = 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900';
      dot = 'bg-blue-500';
    }

    return (
      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${bg}`}>
        <span className={`w-1.5 h-1.5 rounded-full ${dot} animate-pulse`} />
        {severity} • {colorCode}
      </span>
    );
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 75) return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900';
    if (score >= 50) return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-950/40 border-orange-200 dark:border-orange-900';
    if (score >= 25) return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900';
    return 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900';
  };

  return (
    <div className="space-y-4">
      {/* 1. Official Government Warnings (Direct Matches) */}
      {directList.length > 0 ? (
        <div className="space-y-3">
          {directList.map((al) => {
            const isExpanded = expandedAlertId === al.id;
            return (
              <div
                key={al.id}
                className="bg-white dark:bg-slate-900 rounded-xl border border-red-200 dark:border-red-900/60 p-4 shadow-sm transition hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2.5">
                    <div className="p-2 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-100 dark:border-red-900/40 mt-0.5">
                      {getAlertIcon(al.category)}
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-red-600 dark:text-red-400">
                          {t('official_warning') || 'OFFICIAL WARNING'}
                        </span>
                        <span className="text-slate-300 dark:text-slate-600">•</span>
                        <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400">
                          {al.source}
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-slate-900 dark:text-white mt-0.5">
                        {al.title}
                      </h4>
                      <div className="flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        <MapPin className="w-3 h-3 text-slate-400 flex-shrink-0" />
                        <span>{al.location}</span>
                      </div>
                    </div>
                  </div>
                  {getSeverityBadge(al.severity, al.color_code)}
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 mt-3 leading-relaxed">
                  {al.description}
                </p>

                {/* Timing & Validity */}
                <div className="mt-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-850 border border-slate-100 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-300 flex flex-wrap items-center justify-between gap-2">
                  <span className="flex items-center gap-1.5 font-medium">
                    <Clock className="w-3.5 h-3.5 text-primary-500" />
                    <span>{al.start_time} — {al.end_time}</span>
                  </span>
                  {al.duration_text && (
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                      {t('duration') || 'Duration'}: {al.duration_text}
                    </span>
                  )}
                </div>

                {/* Safety Precautions Accordion */}
                {al.safety_precautions && al.safety_precautions.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800">
                    <button
                      onClick={() => toggleExpand(al.id)}
                      className="w-full flex items-center justify-between text-xs font-bold text-primary-600 dark:text-primary-400 hover:underline py-1"
                    >
                      <span className="flex items-center gap-1.5">
                        <Shield className="w-3.5 h-3.5" />
                        {t('safety_precautions') || 'Safety Precautions'} (NDMA Dos & Don'ts)
                      </span>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {isExpanded && (
                      <div className="mt-2 space-y-1.5 p-3 rounded-lg bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/50 dark:border-amber-900/30 text-[11px] text-slate-700 dark:text-slate-300 animate-in fade-in duration-200">
                        {al.safety_precautions.map((step, idx) => (
                          <div key={idx} className="flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                            <span className="leading-snug">{step}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        /* Differentiated No Direct Alert State */
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
              serviceStatus === 'temporarily_unavailable'
                ? 'bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400'
                : 'bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400'
            }`}>
              {serviceStatus === 'temporarily_unavailable' ? (
                <Radio className="w-4 h-4 animate-pulse" />
              ) : (
                <CheckCircle2 className="w-4 h-4" />
              )}
            </div>
            <div className="flex-1">
              <div className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {serviceStatus === 'temporarily_unavailable'
                  ? (t('service_unavailable') || 'Official alert service temporarily unavailable.')
                  : (t('no_official_warnings') || 'No active official warnings for this location.')}
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                {serviceMessage || 'Verified against National Disaster Alert Portal (SACHET / NDMA / IMD).'}
              </p>
            </div>
            {serviceStatus === 'temporarily_unavailable' && onRefresh && (
              <button
                onClick={onRefresh}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                title={t('retry') || 'Retry'}
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* 2. Nearby / Regional Alerts (if user is outside direct polygon but near) */}
      {regionalList.length > 0 && directList.length === 0 && (
        <div className="bg-amber-50/40 dark:bg-amber-950/20 rounded-xl border border-amber-200/60 dark:border-amber-900/40 p-3.5">
          <div className="flex items-center justify-between mb-2">
            <h5 className="text-[11px] font-bold text-amber-800 dark:text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
              <Radio className="w-3 h-3 text-amber-500" />
              {t('regional_alerts') || 'Nearby / Regional Alerts'}
            </h5>
            <span className="text-[10px] text-slate-400">Within 150 km</span>
          </div>
          <div className="space-y-2">
            {regionalList.slice(0, 2).map((ra) => (
              <div key={ra.id} className="text-xs p-2.5 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-100 dark:border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 dark:text-slate-200">{ra.title}</span>
                  {ra.distance_km !== null && (
                    <span className="text-[10px] text-slate-400">{ra.distance_km} km away</span>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  {ra.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. AI Risk Monitoring (Deterministic Hazard Risk Engine) */}
      {aiRisk && (
        <div className="bg-slate-50 dark:bg-slate-850 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
                {t('ai_risk_monitoring') || 'AI Hazard Risk Monitoring'}
              </h4>
            </div>
            <div className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border ${getRiskScoreColor(aiRisk.score)}`}>
              {aiRisk.level} • {aiRisk.score}/100
            </div>
          </div>

          <div className="space-y-2 mt-2.5">
            <div className="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-400">
              <span>{t('expected_window') || 'Expected Window'}:</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{aiRisk.expected_window}</span>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {aiRisk.reason}
            </p>

            {/* Score Progress Bar */}
            <div className="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden mt-2">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  aiRisk.score >= 75 ? 'bg-red-500' : aiRisk.score >= 50 ? 'bg-orange-500' : aiRisk.score >= 25 ? 'bg-amber-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${Math.max(5, aiRisk.score)}%` }}
              />
            </div>

            <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
              <span>{t('confidence') || 'Confidence'}: <strong className="text-slate-500 dark:text-slate-300">{aiRisk.confidence}</strong></span>
              <span className="text-[9px] italic line-clamp-1">{t('disclaimer_label') || 'AI estimate — not an official warning.'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
