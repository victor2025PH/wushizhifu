import React from 'react';
import { Home, Wallet, Clock, User } from 'lucide-react';
import { ViewState, Language, TRANSLATIONS } from '../types';

interface BottomNavProps {
  currentView: ViewState;
  onChange: (view: ViewState) => void;
  lang: Language;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentView, onChange, lang }) => {
  const t = TRANSLATIONS[lang];

  const tabs: { id: ViewState; label: string; icon: React.FC<any> }[] = [
    { id: 'dashboard', label: t.navHome, icon: Home },
    { id: 'wallet', label: t.navWallet, icon: Wallet },
    { id: 'history', label: t.navActivity, icon: Clock },
    { id: 'profile', label: t.navProfile, icon: User },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 z-40 bg-gradient-to-t from-tech-bg via-tech-bg/95 to-transparent pointer-events-none">
      <div className="max-w-md mx-auto pointer-events-auto">
        <div className="bg-white/80 backdrop-blur-xl border border-white/50 shadow-soft rounded-[2rem] p-2 flex justify-between items-center relative overflow-hidden">
          {tabs.map((tab) => {
            const isActive = currentView === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onChange(tab.id)}
                className={`relative flex-1 flex flex-col items-center justify-center py-3 rounded-2xl transition-all duration-300 ${
                  isActive ? 'text-champagne-600' : 'text-tech-sub hover:text-tech-text'
                }`}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-gradient-to-b from-champagne-50 to-transparent opacity-50 rounded-2xl" />
                )}
                <tab.icon
                  className={`w-6 h-6 mb-1 transition-transform duration-300 ${
                    isActive ? 'scale-110' : ''
                  }`}
                  strokeWidth={isActive ? 2.5 : 2}
                />
                <span className={`text-[10px] font-medium ${isActive ? 'font-bold' : ''}`}>
                  {tab.label}
                </span>
                {isActive && (
                   <div className="absolute bottom-1 w-1 h-1 rounded-full bg-champagne-500" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};