import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowDownLeft, ArrowUpRight, Filter } from 'lucide-react';
import { Language, TRANSLATIONS, Transaction } from '../types';

interface HistoryViewProps {
  lang: Language;
  onBack?: () => void;
  isTab?: boolean;
}

// Mock Data
const MOCK_HISTORY: Transaction[] = [
  { id: '1', type: 'topup', amount: 500.00, currency: 'CNY', status: 'success', date: '2023-10-24 14:30', provider: 'alipay' },
  { id: '2', type: 'withdraw', amount: 200.00, currency: 'USDT', status: 'pending', date: '2023-10-24 12:00' },
  { id: '3', type: 'topup', amount: 2000.00, currency: 'CNY', status: 'pending', date: '2023-10-24 10:15', provider: 'wechat' },
  { id: '4', type: 'topup', amount: 100.00, currency: 'CNY', status: 'failed', date: '2023-10-23 09:20', provider: 'alipay' },
  { id: '5', type: 'withdraw', amount: 500.00, currency: 'USDT', status: 'success', date: '2023-10-22 16:45' },
  { id: '6', type: 'topup', amount: 1500.00, currency: 'CNY', status: 'success', date: '2023-10-22 18:45', provider: 'wechat' },
  { id: '7', type: 'topup', amount: 300.00, currency: 'CNY', status: 'success', date: '2023-10-20 11:30', provider: 'alipay' },
];

export const HistoryView: React.FC<HistoryViewProps> = ({ lang, onBack, isTab = false }) => {
  const t = TRANSLATIONS[lang];

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'success': return 'text-green-600 bg-green-50';
      case 'pending': return 'text-orange-500 bg-orange-50';
      case 'failed': return 'text-red-500 bg-red-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  const getStatusText = (status: string) => {
    switch(status) {
      case 'success': return t.success;
      case 'pending': return t.pending;
      case 'failed': return t.failed;
      default: return status;
    }
  };

  const getProviderName = (provider?: string) => {
    if (!provider) return '';
    if (provider === 'alipay') return t.alipay;
    if (provider === 'wechat') return t.wechat;
    return provider;
  }

  return (
    <motion.div 
      className={`flex flex-col h-full ${isTab ? 'pt-6 pb-24' : ''}`}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className={`flex items-center justify-between mb-6 ${!isTab ? 'pt-4' : ''}`}>
        <div className="flex items-center">
          {!isTab && onBack && (
            <button onClick={onBack} className="p-3 bg-white rounded-full shadow-soft hover:shadow-md transition-all text-tech-text mr-4">
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <h2 className={`${isTab ? 'text-2xl font-extrabold' : 'text-xl font-bold'} text-tech-text`}>
            {isTab ? t.navActivity : t.history}
          </h2>
        </div>
        <button className="p-2 text-tech-sub hover:text-tech-primary bg-white rounded-full shadow-sm">
          <Filter className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto pb-6 space-y-3 pr-1">
        {MOCK_HISTORY.map((item, index) => {
          const isTopUp = item.type === 'topup';
          
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center justify-between"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isTopUp ? 'bg-blue-50 text-blue-500' : 'bg-purple-50 text-purple-500'}`}>
                  {isTopUp ? <ArrowDownLeft className="w-5 h-5" /> : <ArrowUpRight className="w-5 h-5" />}
                </div>
                <div>
                  <div className="text-sm font-bold text-tech-text capitalize">
                    {isTopUp 
                      ? `${getProviderName(item.provider)} ${t.topUp}` 
                      : `USDT ${t.withdraw}`}
                  </div>
                  <div className="text-xs text-tech-sub">
                    {item.date}
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className={`font-bold ${isTopUp ? 'text-tech-text' : 'text-tech-text'}`}>
                  {isTopUp ? '+' : '-'}{item.amount.toFixed(2)}
                </div>
                <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${getStatusColor(item.status)}`}>
                  {getStatusText(item.status)}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};