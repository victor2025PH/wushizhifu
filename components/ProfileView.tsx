import React from 'react';
import { motion } from 'framer-motion';
import { Settings, Globe, Shield, Headphones, Info, ChevronRight, LogOut, BadgeCheck } from 'lucide-react';
import { Language, TRANSLATIONS, TelegramUser } from '../types';

interface ProfileViewProps {
  lang: Language;
  user: TelegramUser | null;
  onToggleLang: () => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({ lang, user, onToggleLang }) => {
  const t = TRANSLATIONS[lang];
  const displayName = user?.first_name || t.guest;

  const MenuItem: React.FC<{ icon: React.FC<any>; label: string; value?: string; onClick?: () => void; danger?: boolean }> = ({ icon: Icon, label, value, onClick, danger }) => (
    <button onClick={onClick} className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors first:rounded-t-2xl last:rounded-b-2xl border-b border-gray-100 last:border-0 bg-white">
        <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${danger ? 'bg-red-50 text-red-500' : 'bg-gray-50 text-tech-sub'}`}>
                <Icon className="w-5 h-5" />
            </div>
            <span className={`text-sm font-medium ${danger ? 'text-red-500' : 'text-tech-text'}`}>{label}</span>
        </div>
        <div className="flex items-center space-x-2">
            {value && <span className="text-xs text-tech-sub font-medium">{value}</span>}
            <ChevronRight className="w-4 h-4 text-gray-300" />
        </div>
    </button>
  );

  return (
    <motion.div 
      className="flex flex-col h-full pt-6 pb-24"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
        <header className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-extrabold text-tech-text">{t.navProfile}</h2>
            <button className="p-2 bg-white rounded-full shadow-sm text-tech-text hover:bg-gray-50">
                <Settings className="w-5 h-5" />
            </button>
        </header>

        {/* User Card */}
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-champagne-100 mb-6 flex items-center space-x-4">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-champagne-200 to-white p-1 shadow-gold">
                {user?.photo_url ? (
                    <img src={user.photo_url} alt="Profile" className="w-full h-full rounded-full object-cover" />
                ) : (
                    <div className="w-full h-full bg-white rounded-full flex items-center justify-center text-champagne-600 text-xl font-bold">
                        {displayName[0]}
                    </div>
                )}
            </div>
            <div>
                <h3 className="text-xl font-bold text-tech-text mb-1 flex items-center">
                    {displayName}
                    <BadgeCheck className="w-5 h-5 text-blue-500 ml-1" />
                </h3>
                {user?.username && <p className="text-sm text-tech-sub">@{user.username}</p>}
                <div className="mt-2 inline-flex items-center px-2 py-0.5 rounded bg-blue-50 text-blue-600 text-[10px] font-bold uppercase tracking-wider">
                    {t.verified}
                </div>
            </div>
        </div>

        {/* Menu Groups */}
        <div className="space-y-6">
            <div className="shadow-sm rounded-2xl">
                <MenuItem icon={Globe} label={t.language} value={lang === 'en' ? 'English' : '中文'} onClick={onToggleLang} />
                <MenuItem icon={Shield} label={t.verification} value={t.verified} />
            </div>

            <div className="shadow-sm rounded-2xl">
                <MenuItem icon={Headphones} label={t.support} />
                <MenuItem icon={Info} label={t.about} value="v2.5.0" />
            </div>

            <div className="shadow-sm rounded-2xl">
                <MenuItem icon={LogOut} label={t.logout} danger />
            </div>
        </div>

        <div className="mt-auto text-center">
            <p className="text-[10px] text-gray-300">WuShiPay Tech Ltd. &copy; 2024</p>
        </div>
    </motion.div>
  );
};