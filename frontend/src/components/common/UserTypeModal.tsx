import React from 'react';
import { UserType } from '../../types';
import { useWeather } from '../../contexts/WeatherContext';
import { Check, X } from 'lucide-react';

interface UserTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentType: UserType;
  onSelect: (type: UserType) => void;
}

const ROLES: { type: UserType; icon: string; title: string; desc: string }[] = [
  {
    type: 'General User',
    icon: '🌤',
    title: 'General User',
    desc: 'Daily weather outlook, clothing & umbrella recommendations, 7-day forecast.',
  },
  {
    type: 'Farmer',
    icon: '🌾',
    title: 'Farmer / Agriculture',
    desc: 'Crop weather advisories, rainfall timing, soil moisture, and farming alerts.',
  },
  {
    type: 'Disaster Management',
    icon: '🚨',
    title: 'Disaster Management',
    desc: 'Severe weather alerts, cyclone tracking, flood inundation risk, emergency checklist.',
  },
  {
    type: 'Researcher',
    icon: '🔬',
    title: 'Researcher / Climatologist',
    desc: 'Historical weather records, long-term climate trends, anomaly analysis, data export.',
  },
  {
    type: 'Government / Official',
    icon: '🏛',
    title: 'Government / Official',
    desc: 'District-level alerts, public safety advisories, inter-departmental weather summaries.',
  },
  {
    type: 'Aviation',
    icon: '✈',
    title: 'Aviation',
    desc: 'Horizontal visibility, surface wind shear, cloud ceiling, VFR/IFR flight categories.',
  },
  {
    type: 'Marine',
    icon: '🌊',
    title: 'Marine / Coastal',
    desc: 'Wave height, Beaufort sea state, coastal wind squalls, storm warnings for fishermen.',
  },
  {
    type: 'Student',
    icon: '🎓',
    title: 'Student / Academic',
    desc: 'Atmospheric pressure dynamics, cloud classification, meteorological learning.',
  },
];

export const UserTypeModal: React.FC<UserTypeModalProps> = ({
  isOpen,
  onClose,
  currentType,
  onSelect,
}) => {
  const { t } = useWeather();
  if (!isOpen) return null;

  const roleItems: { type: UserType; icon: string; title: string; desc: string }[] = [
    {
      type: 'General User',
      icon: '🌤',
      title: t('role_general'),
      desc: t('role_general_desc'),
    },
    {
      type: 'Farmer',
      icon: '🌾',
      title: t('role_farmer'),
      desc: t('role_farmer_desc'),
    },
    {
      type: 'Disaster Management',
      icon: '🚨',
      title: t('role_disaster'),
      desc: t('role_disaster_desc'),
    },
    {
      type: 'Researcher',
      icon: '🔬',
      title: t('role_researcher'),
      desc: t('role_researcher_desc'),
    },
    {
      type: 'Government / Official',
      icon: '🏛',
      title: t('role_gov'),
      desc: t('role_gov_desc') || t('role_general_desc'),
    },
    {
      type: 'Aviation',
      icon: '✈',
      title: t('role_aviation'),
      desc: t('role_aviation_desc'),
    },
    {
      type: 'Marine',
      icon: '🌊',
      title: t('role_marine'),
      desc: t('role_marine_desc'),
    },
    {
      type: 'Student',
      icon: '🎓',
      title: t('role_student'),
      desc: t('role_student_desc') || t('role_general_desc'),
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl max-w-2xl w-full p-6 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-md"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400 mb-3">
            <span className="text-2xl">🌦</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t('select_role_prompt')}
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {t('user_mode_label')}: {t('preferences_units')}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {roleItems.map((role) => {
            const isSelected = currentType === role.type;
            return (
              <button
                key={role.type}
                onClick={() => {
                  onSelect(role.type);
                  onClose();
                }}
                className={`flex items-start gap-3 p-3.5 rounded-lg text-left transition-all border ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50/70 dark:bg-primary-950/40 text-primary-900 dark:text-primary-100 shadow-sm'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-850 text-slate-800 dark:text-slate-200'
                }`}
              >
                <span className="text-2xl flex-shrink-0">{role.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm">{role.title}</span>
                    {isSelected && <Check className="w-4 h-4 text-primary-600 dark:text-primary-400" />}
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                    {role.desc}
                  </p>
                </div>
              </button>
            );
          })}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
          >
            {t('continue') || 'Continue'}
          </button>
        </div>
      </div>
    </div>
  );
};
