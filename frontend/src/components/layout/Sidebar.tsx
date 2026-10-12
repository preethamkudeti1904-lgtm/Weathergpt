import React from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { useAuth } from '../../contexts/AuthContext';
import { canAccessAdvisory } from '../../utils/permissions';
import {
  Home,
  CloudSun,
  CalendarDays,
  Map as MapIcon,
  AlertTriangle,
  BarChart3,
  MapPin,
  Bot,
  Sprout,
  Compass,
  Settings,
  ChevronLeft,
  ChevronRight,
  X,
  Layers,
  ShieldAlert,
  Plane,
  Waves
} from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isMobileOpen: boolean;
  onCloseMobile: () => void;
  onOpenRoleModal: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onNavigate,
  isCollapsed,
  onToggleCollapse,
  isMobileOpen,
  onCloseMobile,
  onOpenRoleModal,
}) => {
  const { alerts, t } = useWeather();
  const { user } = useAuth();

  const userType = user?.user_type || 'General User';
  const alertCount = alerts?.alerts?.length || 0;

  const getUserTypeLabel = (type: string) => {
    switch (type) {
      case 'Farmer': return t('role_farmer');
      case 'Disaster Management': return t('role_disaster_mgmt');
      case 'Aviation': return t('role_aviation');
      case 'Marine': return t('role_marine');
      case 'Researcher': return t('role_researcher');
      case 'Student': return t('role_student');
      case 'Government / Official': return t('role_government');
      default: return t('role_general');
    }
  };

  const isFarmer = canAccessAdvisory(user);

  const navItems = [
    { id: 'dashboard', label: t('nav_dashboard'), icon: Home },
    { id: 'current', label: t('nav_current'), icon: CloudSun },
    { id: 'forecast', label: t('nav_forecast'), icon: CalendarDays },
    { id: 'map', label: t('nav_map'), icon: MapIcon },
    { id: 'alerts', label: t('nav_alerts'), icon: AlertTriangle, badge: alertCount },
    { id: 'climate', label: t('nav_climate'), icon: BarChart3 },
    { id: 'locations', label: t('nav_locations'), icon: MapPin },
    { id: 'chat', label: t('nav_ai'), icon: Bot, isHighlight: true },
    ...(isFarmer ? [{ id: 'advisory', label: t('nav_advisory'), icon: Sprout }] : []),
    { id: 'wind-direction', label: t('nav_wind_direction'), icon: Compass },
    { id: 'settings', label: t('nav_settings'), icon: Settings },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 select-none">
      {/* Role Banner / Badge */}
      <div className="p-3 border-b border-slate-100 dark:border-slate-800">
        <button
          onClick={onOpenRoleModal}
          className={`w-full text-left rounded-lg p-2 transition flex items-center gap-2 bg-slate-50 dark:bg-slate-850 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 ${
            isCollapsed ? 'justify-center' : ''
          }`}
          title={`${t('user_mode_label')}: ${getUserTypeLabel(userType)}`}
        >
          <span className="text-lg flex-shrink-0">
            {userType === 'Farmer' ? '🌾' :
             userType === 'Disaster Management' ? '🚨' :
             userType === 'Aviation' ? '✈' :
             userType === 'Marine' ? '🌊' :
             userType === 'Researcher' ? '🔬' :
             userType === 'Student' ? '🎓' :
             userType === 'Government / Official' ? '🏛' : '🌤'}
          </span>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                {t('user_mode_label')}
              </div>
              <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                {getUserTypeLabel(userType)}
              </div>
            </div>
          )}
        </button>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              onClick={() => {
                onNavigate(item.id);
                onCloseMobile();
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-primary-600 text-white shadow-sm'
                  : item.isHighlight
                  ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-primary-900/50'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
              } ${isCollapsed ? 'justify-center px-2' : ''}`}
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : item.isHighlight ? 'text-primary-600 dark:text-primary-400' : 'text-slate-500 dark:text-slate-400'}`} />
              {!isCollapsed && (
                <span className="flex-1 text-left truncate">{item.label}</span>
              )}
              {!isCollapsed && item.badge !== undefined && item.badge > 0 && (
                <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                  isActive ? 'bg-white text-primary-700' : 'bg-amber-500 text-white'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Desktop Collapse Toggle Button */}
      <div className="hidden lg:flex p-2 border-t border-slate-100 dark:border-slate-800 justify-end">
        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:block h-[calc(100vh-4rem)] sticky top-16 transition-all duration-200 z-30 flex-shrink-0 ${
          isCollapsed ? 'w-16' : 'w-60'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop & Sidebar */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm"
            onClick={onCloseMobile}
          />
          <div className="relative w-64 max-w-[80vw] h-full shadow-2xl z-10 animate-slideRight">
            <button
              onClick={onCloseMobile}
              className="absolute top-3 right-3 p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 z-20"
            >
              <X className="w-5 h-5" />
            </button>
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
