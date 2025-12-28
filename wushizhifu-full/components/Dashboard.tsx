import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Wallet, ArrowRight, Zap, Shield, Calculator, Clock, User as UserIcon, BadgeCheck } from 'lucide-react';
import { PaymentProvider, EXCHANGE_RATE_CNY_USDT, Language, TRANSLATIONS, TelegramUser } from '../types';
import { Logo } from './Logo';
import { AlipayGuideModal } from './AlipayGuideModal';
import { WeChatGuideModal } from './WeChatGuideModal';

interface DashboardProps {
  onSelectProvider: (provider: PaymentProvider) => void;
  onOpenCalculator: () => void;
  onOpenHistory: () => void;
  onOpenProfile: () => void;
  lang: Language;
  user: TelegramUser | null;
}

const AlipayIcon = () => (
  <svg viewBox="0 0 1024 1024" fill="currentColor" className="w-8 h-8">
    <path d="M826.8 412h-315v-95h246.5c10.5 0 19-8.5 19-19v-59c0-10.5-8.5-19-19-19H511.8v-72c0-10.5-8.5-19-19-19h-66c-10.5 0-19 8.5-19 19v72H165.2c-10.5 0-19 8.5-19 19v59c0 10.5 8.5 19 19 19h246.6v95h-298c-10.5 0-19 8.5-19 19v56c0 10.5 8.5 19 19 19h455.5c-20.5 45-56.5 83.5-103 111-46.5-39-82.5-88-105-143-3.5-9-14-13-22.5-9.5l-61 24.5c-9 3.5-13.5 13.5-10 22.5 28 68.5 73.5 129.5 131.5 177-89.5 68-196 95-307 97.5-10.5 0-19 8.5-19 19v59.5c0 10 7.5 18.5 17.5 19 157.5-6.5 306-60.5 423-148 102 91.5 199.5 125.5 301.5 125.5 10.5 0 19-8.5 19-19v-91c0-8-5-15-12.5-17.5-75.5-25-156.5-68.5-235-141.5 58.5-47.5 104-106 131.5-171h110.5c10.5 0 19-8.5 19-19v-56c0-10.5-8.5-19-19-19z"/>
  </svg>
);

const WeChatIcon = () => (
  <svg viewBox="0 0 1024 1024" fill="currentColor" className="w-9 h-9">
     <path d="M394.3 194.2c-174 0-315 119.4-315 266.6 0 81.7 43.6 155.8 112 204.5L163.6 750l101-52.8c40.1 11.1 82.8 17.3 127.6 17.3 8.5 0 16.9-0.2 25.2-0.6-5.5-24.3-8.5-49.5-8.5-75.3 0-166.4 155.6-301.4 347.5-301.4 2 0 4.1 0 6.1 0.1C689.4 250.7 550.8 194.2 394.3 194.2z m363.3 259.1c-154.9 0-280.5 104-280.5 232.4 0 128.4 125.6 232.4 280.5 232.4 34.9 0 68.2-5.3 99.4-14.9l79.1 42.3-21-68.8c55.3-38.4 90.8-97.5 90.8-162.8C1038.1 557.3 926.9 453.3 757.6 453.3z"/>
  </svg>
);

export const Dashboard: React.FC<DashboardProps> = ({ 
  onSelectProvider, 
  onOpenCalculator,
  onOpenHistory,
  onOpenProfile,
  lang,
  user
}) => {
  const [showAlipayGuide, setShowAlipayGuide] = useState(false);
  const [showWeChatGuide, setShowWeChatGuide] = useState(false);
  const [showScrollHint, setShowScrollHint] = useState(true);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const t = TRANSLATIONS[lang];
  const displayName = user?.first_name || t.guest;
  const username = user?.username ? `@${user.username}` : '';

  // Hide scroll hint after 5 seconds or when user scrolls
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowScrollHint(false);
    }, 5000);

    const handleScroll = () => {
      setShowScrollHint(false);
    };

    // Listen to window scroll events
    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('touchmove', handleScroll, { passive: true });

    return () => {
      clearTimeout(timer);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('touchmove', handleScroll);
    };
  }, []);

  const handleAlipayClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Alipay button clicked, showing guide modal');
    setShowAlipayGuide(true);
  };

  const handleAlipayConfirm = () => {
    onSelectProvider('alipay');
  };

  const handleWeChatClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('WeChat button clicked, showing guide modal');
    setShowWeChatGuide(true);
  };

  const handleWeChatConfirm = () => {
    onSelectProvider('wechat');
  };

  return (
    <motion.div 
      ref={scrollContainerRef}
      className="flex flex-col h-full pt-6 pb-24" 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      {/* Brand Logo Header */}
      <div className="flex justify-center items-center mb-0 px-1">
        <Logo size="xs" className="drop-shadow-md" />
      </div>

      {/* User Welcome and Total Assets Row */}
      <div className="flex justify-between items-end mb-6 px-1">
        {/* User Info - Clickable */}
        <button onClick={onOpenProfile} className="flex items-center space-x-3 text-left group">
          <div className="relative">
            {/* Premium Gold Gradient Border with Double Ring Effect */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-champagne-200 via-champagne-500 to-champagne-700 p-[2px] shadow-gold group-hover:shadow-lg transition-all duration-300">
              <div className="w-full h-full rounded-full bg-white border-[2px] border-white overflow-hidden flex items-center justify-center">
                {user?.photo_url ? (
                  <img src={user.photo_url} alt="Profile" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                ) : (
                  <UserIcon className="w-6 h-6 text-champagne-600" />
                )}
              </div>
            </div>
            {/* Online Status Dot */}
            <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 border-2 border-white rounded-full shadow-sm"></div>
          </div>
          
          <div className="flex flex-col justify-end pb-0.5">
            <div className="text-xs text-tech-sub font-medium mb-1 group-hover:text-champagne-600 transition-colors">{t.welcome}</div>
            <div className="flex items-center space-x-1">
              <span className="text-lg font-bold text-tech-text leading-none group-hover:text-tech-primary transition-colors">{displayName}</span>
              {user && <BadgeCheck className="w-4 h-4 text-blue-500 fill-blue-50" />}
            </div>
          </div>
        </button>
        
        {/* Total Assets - Aligned Parallel */}
        <div className="flex flex-col items-end pb-0.5">
          <div className="text-[10px] text-tech-sub uppercase tracking-wider mb-1">{t.totalAssets}</div>
          <div className="font-bold text-tech-text text-xl leading-none flex items-baseline">
             0.00 <span className="text-[10px] text-champagne-600 ml-1 font-bold">USDT</span>
          </div>
        </div>
      </div>

      {/* Rate Card */}
      <div className="relative overflow-hidden bg-white/60 backdrop-blur-xl border border-white/50 rounded-3xl p-5 mb-4 shadow-soft group transition-all duration-300 hover:shadow-gold hover:border-champagne-200/60">
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-champagne-200/20 to-tech-primary/10 rounded-full blur-2xl -translate-y-10 translate-x-10" />
        
        <div className="flex justify-between items-center relative z-10 h-full w-full">
          <div className="flex items-center space-x-4 flex-shrink-0">
            <div className="bg-gradient-to-br from-champagne-400 to-champagne-600 p-3 rounded-2xl shadow-gold text-white flex-shrink-0">
              <TrendingUp className="w-5 h-5" strokeWidth={2.5} />
            </div>
            <div className="flex flex-col justify-center">
              <div className="text-xs text-tech-sub font-medium mb-0.5">{t.exchangeRate}</div>
              <div className="text-sm font-bold text-tech-text whitespace-nowrap">{t.cnyToUsdt}</div>
            </div>
          </div>
          
          <div className="text-right flex flex-col justify-center flex-shrink-0">
             <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-gold leading-tight">
               ¥{EXCHANGE_RATE_CNY_USDT.toFixed(2)}
             </div>
             <div className="flex items-center justify-end mt-1 space-x-1">
               <Zap className="w-3 h-3 fill-current text-champagne-600" />
               <span className="text-[10px] text-champagne-600 font-medium whitespace-nowrap">
                 {t.liveUpdate}
               </span>
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
          onClick={handleAlipayClick}
          className="group relative overflow-hidden rounded-3xl bg-white border border-transparent p-6 text-left transition-all duration-500 ease-[cubic-bezier(0.25,0.8,0.25,1)] shadow-soft hover:-translate-y-2 hover:shadow-[0_25px_50px_-12px_rgba(198,156,53,0.4)] hover:border-champagne-300"
        >
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity duration-300">
            <svg viewBox="0 0 24 24" className="w-24 h-24 fill-blue-600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
          </div>
          <div className="relative z-10 flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-[#1677FF] flex items-center justify-center text-white shadow-lg shadow-blue-200 group-hover:scale-105 transition-transform duration-300">
              <AlipayIcon />
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
          onClick={handleWeChatClick}
          className="group relative overflow-hidden rounded-3xl bg-white border border-transparent p-6 text-left transition-all duration-500 ease-[cubic-bezier(0.25,0.8,0.25,1)] shadow-soft hover:-translate-y-2 hover:shadow-[0_25px_50px_-12px_rgba(198,156,53,0.4)] hover:border-champagne-300"
        >
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity duration-300">
            <svg viewBox="0 0 24 24" className="w-24 h-24 fill-green-600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          </div>
          <div className="relative z-10 flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-[#07C160] flex items-center justify-center text-white shadow-lg shadow-green-200 group-hover:scale-105 transition-transform duration-300">
               <WeChatIcon />
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
      
      {/* Footer Text REMOVED */}
      <div className="mt-auto" />

      {/* Scroll Down Hint */}
      <AnimatePresence>
        {showScrollHint && (
          <div className="mt-4 flex flex-col items-center justify-center">
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: 2, duration: 0.5 }}
              className="text-tech-sub text-xs flex items-center space-x-2"
            >
              <motion.span
                animate={{ y: [0, 5, 0] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                className="inline-block text-lg"
              >
                ↓
              </motion.span>
              <span>向下滑动查看更多</span>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Alipay Guide Modal */}
      <AlipayGuideModal
        isOpen={showAlipayGuide}
        onClose={() => setShowAlipayGuide(false)}
        onConfirm={handleAlipayConfirm}
        lang={lang}
      />

      {/* WeChat Guide Modal */}
      <WeChatGuideModal
        isOpen={showWeChatGuide}
        onClose={() => setShowWeChatGuide(false)}
        onConfirm={handleWeChatConfirm}
        lang={lang}
      />
    </motion.div>
  );
};