import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, RefreshCw, Info } from 'lucide-react';
import { PaymentProvider, Language, TRANSLATIONS } from '../types';
import { useExchangeRate } from '../hooks/useExchangeRate';

interface PaymentFormProps {
  provider: PaymentProvider;
  onBack: () => void;
  onSubmit: (amount: number) => void;
  lang: Language;
}

export const PaymentForm: React.FC<PaymentFormProps> = ({ provider, onBack, onSubmit, lang }) => {
  const { rate: exchangeRate } = useExchangeRate();
  const [inputValue, setInputValue] = useState<string>('');
  const [usdtAmount, setUsdtAmount] = useState<number>(0);
  const [isCalculating, setIsCalculating] = useState(false);
  const t = TRANSLATIONS[lang];

  const themeClass = provider === 'alipay' ? 'text-blue-600' : 'text-green-600';
  const providerName = provider === 'alipay' ? t.alipay : t.wechat;

  useEffect(() => {
    setIsCalculating(true);
    const handler = setTimeout(() => {
      const val = parseFloat(inputValue);
      if (!isNaN(val) && val > 0) {
        setUsdtAmount(val / exchangeRate);
      } else {
        setUsdtAmount(0);
      }
      setIsCalculating(false);
    }, 400);

    return () => clearTimeout(handler);
  }, [inputValue, exchangeRate]);

  return (
    <motion.div 
      className="flex flex-col h-full"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      transition={{ type: "spring", bounce: 0, duration: 0.4 }}
    >
      <div className="flex items-center mb-8 pt-4">
        <button onClick={onBack} className="p-3 bg-white rounded-full shadow-soft hover:shadow-md transition-all text-tech-text">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="ml-4">
          <h2 className="text-lg font-bold text-tech-text">{t.topUp}</h2>
          <p className="text-xs text-tech-sub font-medium">{t.via} <span className={`capitalize ${themeClass}`}>{providerName}</span></p>
        </div>
      </div>

      <div className="flex-1 space-y-6">
        <div>
          <label className="block text-xs font-bold text-tech-sub uppercase tracking-wider mb-3 pl-1">
            {t.enterAmount}
          </label>
          
          <div className="relative group">
            <span className="absolute left-6 top-1/2 -translate-y-1/2 text-2xl text-tech-sub font-light group-focus-within:text-tech-primary transition-colors">¥</span>
            <input
              type="number"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={t.inputPlaceholder}
              className="w-full bg-tech-input border-2 border-transparent rounded-3xl py-6 pl-12 pr-6 text-3xl font-bold text-tech-text placeholder-gray-300 outline-none transition-all focus:bg-white focus:border-champagne-300 focus:shadow-soft"
              autoFocus
            />
          </div>
        </div>

        {/* Calculation Result Card */}
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-champagne-100">
          <div className="flex justify-between items-center mb-3">
            <span className="text-xs font-medium text-tech-sub uppercase">{t.estimatedReceipt}</span>
            {isCalculating && <RefreshCw className="w-4 h-4 text-champagne-500 animate-spin" />}
          </div>
          
          <div className="flex items-baseline space-x-2 mb-4">
            <span className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-gold">
              {usdtAmount.toFixed(2)}
            </span>
            <span className="text-xl font-bold text-champagne-600">USDT</span>
          </div>
          
          <div className="flex items-center p-3 bg-champagne-50 rounded-xl border border-champagne-200/50">
             <Info className="w-4 h-4 text-champagne-500 mr-2" />
             <span className="text-xs text-tech-sub font-medium">{t.currentRate}: 1 USDT ≈ {exchangeRate.toFixed(2)} CNY</span>
          </div>
        </div>
      </div>

      <div className="pb-8">
        <button
          disabled={usdtAmount <= 0 || isCalculating}
          onClick={() => onSubmit(parseFloat(inputValue))}
          className={`
            w-full py-5 rounded-3xl font-bold text-lg shadow-lg shadow-champagne-500/20 transition-all active:scale-[0.98]
            ${usdtAmount > 0 
              ? 'bg-gradient-gold text-white hover:shadow-gold' 
              : 'bg-tech-input text-gray-400 cursor-not-allowed shadow-none'}
          `}
        >
          {t.generateLink}
        </button>
      </div>
    </motion.div>
  );
};