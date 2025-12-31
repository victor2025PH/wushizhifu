import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Globe, Shield, Headphones, Info, ChevronRight, LogOut, BadgeCheck, ArrowLeft, Zap, Lock, Award } from 'lucide-react';
import { Language, TRANSLATIONS, TelegramUser } from '../types';
import { Logo } from './Logo';
import { openSupportChat, assignCustomerService, CustomerServiceAssignmentResult } from '../utils/supportService';
import { CustomerServiceModal } from './CustomerServiceModal';

interface ProfileViewProps {
  lang: Language;
  user: TelegramUser | null;
  onToggleLang: () => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({ lang, user, onToggleLang }) => {
  const [showAbout, setShowAbout] = useState(false);
  const [showCustomerServiceModal, setShowCustomerServiceModal] = useState(false);
  const [customerServiceResult, setCustomerServiceResult] = useState<CustomerServiceAssignmentResult | null>(null);
  const [isAssigningService, setIsAssigningService] = useState(false);
  const t = TRANSLATIONS[lang];
  const displayName = user?.first_name || t.guest;

  const MenuItem: React.FC<{ icon: React.FC<any>; label: string; value?: string; onClick?: () => void; danger?: boolean }> = ({ icon: Icon, label, value, onClick, danger }) => (
    <button onClick={onClick} className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors first:rounded-t-2xl last:rounded-b-2xl border-b border-gray-100 last:border-0 bg-white group">
        <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg transition-colors ${danger ? 'bg-red-50 text-red-500' : 'bg-gray-50 text-tech-sub group-hover:bg-champagne-50 group-hover:text-champagne-600'}`}>
                <Icon className="w-5 h-5" />
            </div>
            <span className={`text-sm font-medium ${danger ? 'text-red-500' : 'text-tech-text'}`}>{label}</span>
        </div>
        <div className="flex items-center space-x-2">
            {value && <span className="text-xs text-tech-sub font-medium group-hover:text-champagne-600 transition-colors">{value}</span>}
            <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-champagne-400" />
        </div>
    </button>
  );

  // About Page Sub-View
  if (showAbout) {
    return (
      <motion.div 
        className="flex flex-col h-full pt-6 pb-24"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 50 }}
      >
        <div className="flex items-center mb-6 pt-2">
          <button onClick={() => setShowAbout(false)} className="p-3 bg-white rounded-full shadow-soft hover:shadow-md transition-all text-tech-text mr-4">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h2 className="text-xl font-bold text-tech-text">{t.aboutTitle}</h2>
        </div>

        <div className="flex-1 overflow-y-auto pr-1 pb-4">
          {/* Brand Header */}
          <div className="flex flex-col items-center justify-center mb-8 mt-4">
            <div className="w-20 h-20 bg-gradient-gold rounded-2xl flex items-center justify-center shadow-gold mb-4 rotate-3">
               <Logo size="xl" className="drop-shadow-lg" />
            </div>
            <h1 className="text-2xl font-extrabold text-tech-text tracking-tight">{t.appName}</h1>
            <span className="px-3 py-1 bg-champagne-50 text-champagne-700 text-xs font-bold rounded-full border border-champagne-200 mt-2">
              Version 1.5.0
            </span>
          </div>

          {/* Company Description */}
          <div className="bg-white rounded-3xl p-6 shadow-soft border border-champagne-100 mb-6">
            <p className="text-sm text-tech-sub leading-relaxed text-justify">
              {t.companyDesc}
            </p>
          </div>

          {/* Key Features */}
          <div className="space-y-4 mb-8">
            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-start space-x-4">
               <div className="p-3 bg-blue-50 rounded-xl text-blue-600 shrink-0">
                 <Zap className="w-6 h-6" fill="currentColor" fillOpacity={0.2} />
               </div>
               <div>
                 <h3 className="font-bold text-tech-text text-sm mb-1">{t.feature1Title}</h3>
                 <p className="text-xs text-tech-sub leading-snug">{t.feature1Desc}</p>
               </div>
            </div>

            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-start space-x-4">
               <div className="p-3 bg-green-50 rounded-xl text-green-600 shrink-0">
                 <Lock className="w-6 h-6" fill="currentColor" fillOpacity={0.2} />
               </div>
               <div>
                 <h3 className="font-bold text-tech-text text-sm mb-1">{t.feature2Title}</h3>
                 <p className="text-xs text-tech-sub leading-snug">{t.feature2Desc}</p>
               </div>
            </div>

            <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-start space-x-4">
               <div className="p-3 bg-purple-50 rounded-xl text-purple-600 shrink-0">
                 <Award className="w-6 h-6" fill="currentColor" fillOpacity={0.2} />
               </div>
               <div>
                 <h3 className="font-bold text-tech-text text-sm mb-1">{t.feature3Title}</h3>
                 <p className="text-xs text-tech-sub leading-snug">{t.feature3Desc}</p>
               </div>
            </div>
          </div>

          <div className="text-center space-y-2 mb-8">
            <p className="text-xs text-gray-400">
               Terms of Service • Privacy Policy
            </p>
            <p className="text-[10px] text-gray-300 font-medium">
              {t.techLtd} &copy; 2024
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  // Main Profile View
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
                <MenuItem 
                    icon={Headphones} 
                    label={t.support} 
                    onClick={async () => {
                        // 显示加载状态
                        setIsAssigningService(true);
                        setShowCustomerServiceModal(true);
                        
                        // 分配客服账号
                        const result = await assignCustomerService();
                        setCustomerServiceResult(result);
                        setIsAssigningService(false);
                    }}
                />
                <MenuItem icon={Info} label={t.about} value="v1.5.0" onClick={() => setShowAbout(true)} />
            </div>

            <div className="shadow-sm rounded-2xl">
                <MenuItem icon={LogOut} label={t.logout} danger />
            </div>
        </div>

        <div className="mt-auto text-center">
            <p className="text-[10px] text-gray-300">{t.techLtd} &copy; 2024</p>
        </div>

        {/* Customer Service Modal */}
        <CustomerServiceModal
          isOpen={showCustomerServiceModal}
          onClose={() => {
            setShowCustomerServiceModal(false);
            setCustomerServiceResult(null);
          }}
          serviceAccount={customerServiceResult?.service_account || null}
          assignmentMethod={customerServiceResult?.assignment_method}
          error={customerServiceResult?.error}
          onContact={() => {
            if (customerServiceResult?.service_account) {
              openSupportChat(customerServiceResult.service_account);
            }
          }}
          onContactAdmin={() => {
            openSupportChat('wushizhifu_jianglai');
          }}
          lang={lang}
        />
    </motion.div>
  );
};