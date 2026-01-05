import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Delete, ArrowRightLeft } from 'lucide-react';
import { Language, TRANSLATIONS } from '../types';
import { useExchangeRate } from '../hooks/useExchangeRate';

interface CalculatorModalProps {
  lang: Language;
  onClose: () => void;
}

export const CalculatorModal: React.FC<CalculatorModalProps> = ({ lang, onClose }) => {
  const t = TRANSLATIONS[lang];
  const { rate: exchangeRate } = useExchangeRate();
  const [input, setInput] = useState('0');
  const [mode, setMode] = useState<'CNY_TO_USDT' | 'USDT_TO_CNY'>('CNY_TO_USDT');

  const handleNum = (num: string) => {
    if (input === '0' && num !== '.') {
      setInput(num);
    } else {
      if (num === '.' && input.includes('.')) return;
      if (input.length < 10) setInput(input + num);
    }
  };

  const handleDelete = () => {
    if (input.length === 1) setInput('0');
    else setInput(input.slice(0, -1));
  };

  const handleClear = () => setInput('0');

  const calculateResult = () => {
    const val = parseFloat(input);
    if (isNaN(val)) return '0.00';
    
    if (mode === 'CNY_TO_USDT') {
      return (val / exchangeRate).toFixed(2);
    } else {
      return (val * exchangeRate).toFixed(2);
    }
  };

  const toggleMode = () => {
    setMode(prev => prev === 'CNY_TO_USDT' ? 'USDT_TO_CNY' : 'CNY_TO_USDT');
    setInput('0');
  };

  return (
    <motion.div 
      className="fixed inset-0 z-40 flex items-end sm:items-center justify-center sm:p-4 bg-black/60 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="w-full max-w-sm bg-white rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl border-t border-champagne-200"
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        exit={{ y: "100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-bold text-tech-text flex items-center">
            {t.calculator}
            <span className="ml-2 text-xs bg-champagne-100 text-champagne-700 px-2 py-0.5 rounded-full">
              {t.rate}: {exchangeRate.toFixed(2)}
            </span>
          </h3>
          <button onClick={onClose} className="p-2 bg-gray-100 rounded-full hover:bg-gray-200">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Display */}
        <div className="bg-tech-bg rounded-2xl p-4 mb-6 border border-tech-border">
          <div className="flex justify-between text-tech-sub text-xs uppercase font-bold mb-1">
            <span>{mode === 'CNY_TO_USDT' ? 'CNY' : 'USDT'}</span>
            <button onClick={toggleMode} className="flex items-center text-tech-primary hover:text-tech-secondary">
              <ArrowRightLeft className="w-3 h-3 mr-1" /> {t.switchMode}
            </button>
          </div>
          <div className="text-right text-3xl font-bold text-tech-text tracking-tight mb-2 truncate">
            {input}
          </div>
          <div className="h-px w-full bg-gray-200 mb-2" />
          <div className="text-right text-xl font-bold text-champagne-600 truncate">
            = {calculateResult()} <span className="text-xs text-champagne-400">{mode === 'CNY_TO_USDT' ? 'USDT' : 'CNY'}</span>
          </div>
        </div>

        {/* Keypad */}
        <div className="grid grid-cols-4 gap-3">
          {['7', '8', '9'].map(n => (
            <button key={n} onClick={() => handleNum(n)} className="p-4 rounded-2xl bg-gray-50 text-xl font-bold text-tech-text hover:bg-gray-100 active:scale-95 transition-all shadow-sm">
              {n}
            </button>
          ))}
          <button onClick={handleDelete} className="p-4 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center hover:bg-red-100 active:scale-95 shadow-sm">
            <Delete className="w-6 h-6" />
          </button>

          {['4', '5', '6'].map(n => (
            <button key={n} onClick={() => handleNum(n)} className="p-4 rounded-2xl bg-gray-50 text-xl font-bold text-tech-text hover:bg-gray-100 active:scale-95 transition-all shadow-sm">
              {n}
            </button>
          ))}
          <button onClick={handleClear} className="p-4 rounded-2xl bg-orange-50 text-orange-500 font-bold hover:bg-orange-100 active:scale-95 shadow-sm">
            C
          </button>

          {['1', '2', '3'].map(n => (
            <button key={n} onClick={() => handleNum(n)} className="p-4 rounded-2xl bg-gray-50 text-xl font-bold text-tech-text hover:bg-gray-100 active:scale-95 transition-all shadow-sm">
              {n}
            </button>
          ))}
          <button onClick={() => handleNum('.')} className="row-span-2 p-4 rounded-2xl bg-gray-50 text-xl font-bold text-tech-text hover:bg-gray-100 active:scale-95 shadow-sm flex items-center justify-center">
            .
          </button>

          <button onClick={() => handleNum('0')} className="col-span-3 p-4 rounded-2xl bg-gray-50 text-xl font-bold text-tech-text hover:bg-gray-100 active:scale-95 shadow-sm">
            0
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};