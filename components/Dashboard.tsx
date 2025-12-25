import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Wallet, ArrowRight, Zap, Shield, Calculator, Clock, User as UserIcon, BadgeCheck } from 'lucide-react';
import { PaymentProvider, EXCHANGE_RATE_CNY_USDT, Language, TRANSLATIONS, TelegramUser } from '../types';

interface DashboardProps {
  onSelectProvider: (provider: PaymentProvider) => void;
  onOpenCalculator: () => void;
  onOpenHistory: () => void;
  lang: Language;
  user: TelegramUser | null;
}

export const Dashboard: React.FC<DashboardProps> = ({ 
  onSelectProvider, 
  onOpenCalculator,
  onOpenHistory,
  lang,
  user
}) => {
  const t = TRANSLATIONS[lang];
  const displayName = user?.first_name || t.guest;
  const username = user?.username ? `@${user.username}` : '';

  return (
    <motion.div 
      className="flex flex-col h-full pt-6 pb-24" // Added pb-24 for bottom nav
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      {/* Header with User Info */}
      <header className="flex justify-between items-start mb-6">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-champagne-200 to-white p-0.5 shadow-gold overflow-hidden">
              {user?.photo_url ? (
                <img src={user.photo_url} alt="Profile" className="w-full h-full rounded-full object-cover" />
              ) : (
                <div className="w-full h-full bg-white rounded-full flex items-center justify-center text-champagne-600">
                  <UserIcon className="w-7 h-7" />
                </div>
              )}
            </div>
            {/* Online/Verified Indicator */}
            <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
          </div>
          
          <div className="flex flex-col justify-center">
            <div className="text-xs text-tech-sub font-medium mb-0.5">{t.welcome}</div>
            <div className="flex items-center space-x-1">
              <span className="text-lg font-bold text-tech-text leading-tight">{displayName}</span>
              {user && <BadgeCheck className="w-4 h-4 text-blue-500 fill-blue-50" />}
            </div>
            {username && (
              <div className="text-xs text-tech-primary font-medium opacity-80">{username}</div>
            )}
          </div>
        </div>
        
        {/* Total Assets Mini */}
        <div className="text-right bg-white px-3 py-2 rounded-2xl shadow-sm border border-champagne-100/50">
          <div className="text-[10px] text-tech-sub uppercase tracking-wider mb-0.5">{t.totalAssets}</div>
          <div className="font-bold text-tech-text text-lg leading-none">0.00 <span className="text-[10px] text-champagne-600 align-top">USDT</span></div>
        </div>
      </header>

      {/* Rate Card */}
      <div className="relative overflow-hidden bg-white/60 backdrop-blur-xl border border-white/50 rounded-3xl p-5 mb-4 shadow-soft group transition-all duration-300 hover:shadow-gold hover:border-champagne-200/60">
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-champagne-200/20 to-tech-primary/10 rounded-full blur-2xl -translate-y-10 translate-x-10" />
        
        <div className="flex justify-between items-center relative z-10">
          <div className="flex items-center space-x-4">
            <div className="bg-gradient-to-br from-champagne-400 to-champagne-600 p-3 rounded-2xl shadow-gold text-white">
              <TrendingUp className="w-5 h-5" strokeWidth={2.5} />
            </div>
            <div>
              <div className="text-xs text-tech-sub font-medium">{t.exchangeRate}</div>
              <div className="text-sm font-bold text-tech-text">{t.cnyToUsdt}</div>
            </div>
          </div>
          <div className="text-right">
             <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-gold">
               ¥{EXCHANGE_RATE_CNY_USDT.toFixed(2)}
             </div>
             <div className="text-[10px] text-champagne-600 font-medium flex items-center justify-end">
               <Zap className="w-3 h-3 mr-0.5 fill-current" />
               {t.liveUpdate}
             </div>
          </div>
        </div>
      </div>

      {/* Quick Tools Row */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <button 
          onClick={onOpenCalculator}
          className="bg-white p-3 rounded-2xl shadow-sm border border-transparent hover:border-champagne-200 hover:shadow-gold transition-all flex items-center justify-center space-x-2 group"
        >
          <div className="bg-tech-bg p-2 rounded-xl group-hover:bg-champagne-50 transition-colors">
            <Calculator className="w-4 h-4 text-tech-sub group-hover:text-champagne-600" />
          </div>
          <span className="text-sm font-semibold text-tech-text">{t.calculator}</span>
        </button>
        <button 
          onClick={onOpenHistory}
          className="bg-white p-3 rounded-2xl shadow-sm border border-transparent hover:border-champagne-200 hover:shadow-gold transition-all flex items-center justify-center space-x-2 group"
        >
          <div className="bg-tech-bg p-2 rounded-xl group-hover:bg-champagne-50 transition-colors">
            <Clock className="w-4 h-4 text-tech-sub group-hover:text-champagne-600" />
          </div>
          <span className="text-sm font-semibold text-tech-text">{t.history}</span>
        </button>
      </div>

      {/* Payment Providers */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-tech-text">{t.selectChannel}</h3>
        <span className="text-xs text-champagne-700 bg-champagne-50 px-2 py-1 rounded-full border border-champagne-200 shadow-sm">
          {t.instant}
        </span>
      </div>
      
      <div className="grid grid-cols-1 gap-4">
        {/* Alipay Card */}
        <button 
          onClick={() => onSelectProvider('alipay')}
          className="group relative overflow-hidden rounded-3xl bg-white border border-transparent p-6 text-left transition-all duration-300 ease-out active:scale-[0.98] shadow-soft hover:-translate-y-1 hover:shadow-[0_20px_40px_-15px_rgba(198,156,53,0.3)] hover:border-champagne-200"
        >
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity duration-300">
            <svg viewBox="0 0 24 24" className="w-24 h-24 fill-blue-600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
          </div>
          <div className="relative z-10 flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 font-bold text-2xl group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300 shadow-sm group-hover:shadow-blue-200">
              支
            </div>
            <div>
              <h3 className="text-lg font-bold text-tech-text mb-0.5 group-hover:text-blue-600 transition-colors">{t.alipay}</h3>
              <p className="text-xs text-tech-sub font-medium flex items-center">
                {t.fastSecure} <ArrowRight className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 text-blue-500 transition-all -translate-x-2 group-hover:translate-x-0" />
              </p>
            </div>
          </div>
        </button>

        {/* WeChat Pay Card */}
        <button 
          onClick={() => onSelectProvider('wechat')}
          className="group relative overflow-hidden rounded-3xl bg-white border border-transparent p-6 text-left transition-all duration-300 ease-out active:scale-[0.98] shadow-soft hover:-translate-y-1 hover:shadow-[0_20px_40px_-15px_rgba(198,156,53,0.3)] hover:border-champagne-200"
        >
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity duration-300">
            <svg viewBox="0 0 24 24" className="w-24 h-24 fill-green-600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          </div>
          <div className="relative z-10 flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-green-50 flex items-center justify-center text-green-600 font-bold text-2xl group-hover:bg-green-600 group-hover:text-white transition-colors duration-300 shadow-sm group-hover:shadow-green-200">
              微
            </div>
            <div>
              <h3 className="text-lg font-bold text-tech-text mb-0.5 group-hover:text-green-600 transition-colors">{t.wechat}</h3>
              <p className="text-xs text-tech-sub font-medium flex items-center">
                {t.verifiedMerchant} <ArrowRight className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 text-green-500 transition-all -translate-x-2 group-hover:translate-x-0" />
              </p>
            </div>
          </div>
        </button>
      </div>
      
      <div className="mt-auto pb-4 pt-8 flex justify-center">
        <div className="flex items-center space-x-2 px-4 py-2 bg-white/40 rounded-full backdrop-blur-sm border border-champagne-200/50">
          <Shield className="w-3 h-3 text-champagne-500" />
          <p className="text-[10px] text-tech-sub font-medium uppercase tracking-wide">
            {t.secureGateway} v2.5
          </p>
        </div>
      </div>
    </motion.div>
  );
};