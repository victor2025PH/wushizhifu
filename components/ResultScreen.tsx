import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Clock, Copy, ExternalLink, X, Smartphone } from 'lucide-react';
import { PaymentProvider, Language, TRANSLATIONS } from '../types';

interface ResultScreenProps {
  provider: PaymentProvider;
  amount: number;
  onClose: () => void;
  lang: Language;
}

export const ResultScreen: React.FC<ResultScreenProps> = ({ provider, amount, onClose, lang }) => {
  const [timeLeft, setTimeLeft] = useState(15 * 60);
  const t = TRANSLATIONS[lang];

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleJump = () => {
    const url = provider === 'alipay' 
      ? `alipays://platformapi/startapp?appId=20000067&url=https%3A%2F%2Fmock-pay-url.com` 
      : `weixin://dl/business/?t=mocktoken`;
    
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.openLink(url);
    } else {
      window.open(url, '_blank');
    }
  };

  const providerName = provider === 'alipay' ? t.alipay : t.wechat;
  // Use localized provider name for the button label as well
  const appName = providerName; 

  return (
    <motion.div 
      className="flex flex-col h-full pt-6 text-center"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute top-4 right-4">
        <button onClick={onClose} className="p-2 bg-white rounded-full shadow-sm text-gray-400 hover:text-tech-text transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="mb-6 flex justify-center mt-4">
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", damping: 12 }}
          className="w-24 h-24 bg-champagne-50 rounded-full flex items-center justify-center relative border border-champagne-200"
        >
          <div className="absolute inset-0 bg-champagne-400/20 rounded-full animate-ping" />
          <Check className="w-10 h-10 text-champagne-600" strokeWidth={3} />
        </motion.div>
      </div>

      <h2 className="text-2xl font-extrabold text-tech-text mb-2">{t.orderCreated}</h2>
      <p className="text-tech-sub text-sm mb-8 px-8">
        {t.orderDesc}
      </p>

      {/* Timer Pill */}
      <div className="flex justify-center mb-8">
        <div className="bg-gradient-luxury text-white px-5 py-2 rounded-full flex items-center space-x-2 shadow-lg border border-champagne-500/30">
          <Clock className="w-4 h-4 text-champagne-400" />
          <span className="font-mono font-bold tracking-widest text-lg text-champagne-100">
            {formatTime(timeLeft)}
          </span>
        </div>
      </div>

      {/* Details Card */}
      <div className="bg-white rounded-3xl p-6 mb-6 text-left space-y-4 shadow-soft border border-champagne-200/50">
        <div className="flex justify-between items-center pb-4 border-b border-gray-100">
          <span className="text-sm text-tech-sub font-medium">{t.amountToPay}</span>
          <span className="font-bold text-2xl text-transparent bg-clip-text bg-gradient-gold">¥ {amount.toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-tech-sub font-medium">{t.channel}</span>
          <div className="flex items-center space-x-2">
            <span className={`font-bold capitalize ${provider === 'alipay' ? 'text-blue-600' : 'text-green-600'}`}>
              {providerName}
            </span>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-tech-sub font-medium">{t.orderId}</span>
          <button className="flex items-center space-x-1 bg-gray-50 px-2 py-1 rounded-lg hover:bg-gray-100 transition-colors">
            <span className="font-mono text-xs text-gray-600">WS-88239102</span>
            <Copy className="w-3 h-3 text-gray-400" />
          </button>
        </div>
      </div>

      <div className="mt-auto pb-8 space-y-4">
        <button
          onClick={handleJump}
          className={`
            w-full py-4 rounded-3xl font-bold text-lg shadow-lg flex items-center justify-center space-x-2 text-white transition-transform active:scale-[0.98]
            ${provider === 'alipay' ? 'bg-[#1677FF] shadow-blue-200' : 'bg-[#07C160] shadow-green-200'}
          `}
        >
          <Smartphone className="w-5 h-5" />
          <span>{t.openApp.replace('{app}', appName)}</span>
          <ExternalLink className="w-4 h-4 opacity-70" />
        </button>
        
        <p className="text-[10px] text-tech-sub px-8 text-center leading-relaxed">
          {t.secureFooter}
        </p>
      </div>
    </motion.div>
  );
};