import React, { useState } from 'react';
import { TopNav } from './TopNav';
import { Sidebar } from './Sidebar';
import { UserTypeModal } from '../common/UserTypeModal';
import { LocationDebugPanel } from '../common/LocationDebugPanel';
import { useAuth } from '../../contexts/AuthContext';
import { UserType } from '../../types';

interface LayoutProps {
  children: React.ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, currentPage, onNavigate }) => {
  const { user, setUserType } = useAuth();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);

  const currentUserType = user?.user_type || 'General User';

  const handleRoleSelect = (type: UserType) => {
    setUserType(type);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <TopNav
        onOpenMobileNav={() => setIsMobileNavOpen(true)}
        onOpenRoleModal={() => setIsRoleModalOpen(true)}
        onNavigate={onNavigate}
      />

      {/* Body: Sidebar + Main Content */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar
          currentPage={currentPage}
          onNavigate={onNavigate}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          isMobileOpen={isMobileNavOpen}
          onCloseMobile={() => setIsMobileNavOpen(false)}
          onOpenRoleModal={() => setIsRoleModalOpen(true)}
        />

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* User Type Selection Modal */}
      <UserTypeModal
        isOpen={isRoleModalOpen}
        onClose={() => setIsRoleModalOpen(false)}
        currentType={currentUserType}
        onSelect={handleRoleSelect}
      />

      {/* Developer Location Diagnostic Section (Section 25) */}
      <LocationDebugPanel />
    </div>
  );
};
