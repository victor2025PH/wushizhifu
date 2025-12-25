import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Copy, ArrowDown, ArrowUp, RefreshCw, Layers } from 'lucide-react';
import { Language, TRANSLATIONS, TelegramUser } from '../types';

interface WalletViewProps {
  lang: Language;
  user: TelegramUser | null;
}

export const WalletView: React.FC<WalletViewProps> = ({ lang, user }) => {
  const t = TRANSLATIONS[lang];
  const displayName = user?.first_name ? user.first_name.toUpperCase() : 'GUEST USER';

  return (
    <motion.div 
      className="flex flex-col h-full pt-6 pb-24"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <header className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-extrabold text-tech-text">{t.navWallet}</h2>
        <div className="px-3 py-1 bg-green-50 rounded-full border border-green-100 flex items-center space-x-1">
            <ShieldCheck className="w-3 h-3 text-green-600" />
            <span className="text-xs font-bold text-green-700">{t.high}</span>
        </div>
      </header>

      {/* Virtual Card */}
      <div className="relative w-full aspect-[1.6/1] rounded-3xl overflow-hidden mb-8 shadow-2xl group transition-transform hover:scale-[1.02]">
        {/* Card Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-black" />
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />
        <div className="absolute top-0 right-0 w-64 h-64 bg-champagne-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        
        <div className="relative z-10 p-6 flex flex-col justify-between h-full text-white">
            <div className="flex justify-between items-start">
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center">
                        <Layers className="w-4 h-4 text-champagne-400" />
                    </div>
                    <span className="font-bold tracking-wider text-sm opacity-80">{t.appName}</span>
                </div>
                <span className="font-mono text-xl italic font-bold text-champagne-400">{t.premium}</span>
            </div>

            <div className="space-y-1">
                <div className="text-xs text-gray-400 uppercase tracking-widest">{t.totalAssets} (USDT)</div>
                <div className="text-3xl font-mono font-bold tracking-tight text-white drop-shadow-lg">
                    0.00
                </div>
            </div>

            <div className="flex justify-between items-end">
                <div className="font-mono text-sm tracking-widest text-gray-400">
                    {displayName}
                </div>
                <div className="w-10 h-6 bg-white/20 rounded flex items-center justify-center backdrop-blur-sm">
                    <div className="w-3 h-3 bg-red-500 rounded-full opacity-80 mr-[-4px]" />
                    <div className="w-3 h-3 bg-yellow-500 rounded-full opacity-80" />
                </div>
            </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
            { icon: ArrowDown, label: t.receive, color: 'text-blue-600', bg: 'bg-blue-50' },
            { icon: ArrowUp, label: t.send, color: 'text-purple-600', bg: 'bg-purple-50' },
            { icon: RefreshCw, label: t.swap, color: 'text-champagne-600', bg: 'bg-champagne-50' },
        ].map((action, i) => (
            <button key={i} className="flex flex-col items-center space-y-2 group">
                <div className={`w-14 h-14 rounded-2xl ${action.bg} flex items-center justify-center shadow-sm group-hover:shadow-md transition-all`}>
                    <action.icon className={`w-6 h-6 ${action.color}`} />
                </div>
                <span className="text-xs font-medium text-tech-sub group-hover:text-tech-text">{action.label}</span>
            </button>
        ))}
      </div>

      {/* Info List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-tech-text px-1">{t.myAssets}</h3>
        
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center justify-between">
            <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-[#26A17B] flex items-center justify-center text-white font-bold text-xs">
                    T
                </div>
                <div>
                    <div className="text-sm font-bold text-tech-text">USDT</div>
                    <div className="text-xs text-tech-sub">{t.tetherUsd}</div>
                </div>
            </div>
            <div className="text-right">
                <div className="font-bold text-tech-text">0.00</div>
                <div className="text-xs text-tech-sub">≈ ¥0.00</div>
            </div>
        </div>

        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 space-y-3">
            <div className="flex justify-between items-center text-sm">
                <span className="text-tech-sub">{t.network}</span>
                <span className="font-medium text-tech-text bg-gray-100 px-2 py-0.5 rounded text-xs">TRC20</span>
            </div>
            <div className="h-px bg-gray-100" />
            <div className="flex justify-between items-center text-sm">
                <span className="text-tech-sub">{t.depositAddress}</span>
                <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs text-tech-text">T9...xYz</span>
                    <Copy className="w-3 h-3 text-champagne-600" />
                </div>
            </div>
        </div>
      </div>

    </motion.div>
  );
};