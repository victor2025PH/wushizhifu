import React, { useEffect, useState } from 'react';
import { TickerItem } from '../types';
import { ShieldAlert, Wallet, UserPlus } from 'lucide-react';

const generateRandomData = (): TickerItem => {
  const types: Array<TickerItem['type']> = ['withdrawal', 'defense', 'new_user'];
  const type = types[Math.floor(Math.random() * types.length)];
  const id = Math.random().toString(36).substring(7);
  
  let text = '';
  switch (type) {
    case 'withdrawal':
      text = `用户 ${Math.floor(Math.random() * 90) + 10}** 刚刚提现 ${Math.floor(Math.random() * 500) + 50} USDT`;
      break;
    case 'defense':
      text = `已拦截投诉：商户 ID 88${Math.floor(Math.random() * 99)} 避免了风控冻结`;
      break;
    case 'new_user':
      text = `新商户入驻：${Math.floor(Math.random() * 5) + 1}分钟前`;
      break;
  }

  return {
    id,
    text,
    type,
    timestamp: new Date().toLocaleTimeString(),
  };
};

export const LiveTicker: React.FC = () => {
  const [items, setItems] = useState<TickerItem[]>([]);

  useEffect(() => {
    // Initialize with some data
    const initialData = Array.from({ length: 10 }, generateRandomData);
    setItems(initialData);
  }, []);

  const getIcon = (type: TickerItem['type']) => {
    switch (type) {
      case 'withdrawal': return <Wallet className="w-4 h-4 text-green-600 dark:text-green-400" />;
      case 'defense': return <ShieldAlert className="w-4 h-4 text-red-600 dark:text-red-400" />;
      case 'new_user': return <UserPlus className="w-4 h-4 text-blue-600 dark:text-brand-blue" />;
    }
  };

  return (
    <div className="w-full bg-slate-100 dark:bg-slate-900/50 border-y border-slate-200 dark:border-white/5 py-3 overflow-hidden backdrop-blur-sm relative z-20 transition-colors duration-300">
      <div className="max-w-7xl mx-auto flex items-center relative">
        <div className="absolute left-0 w-20 h-full bg-gradient-to-r from-slate-100 dark:from-slate-950 to-transparent z-10 pointer-events-none transition-colors duration-300"></div>
        <div className="absolute right-0 w-20 h-full bg-gradient-to-l from-slate-100 dark:from-slate-950 to-transparent z-10 pointer-events-none transition-colors duration-300"></div>
        
        <div className="flex gap-8 animate-scroll whitespace-nowrap">
          {/* Double the list to create seamless loop */}
          {[...items, ...items].map((item, index) => (
            <div key={`${item.id}-${index}`} className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 bg-white dark:bg-white/5 px-4 py-1.5 rounded-full border border-slate-200 dark:border-white/5 shadow-sm dark:shadow-none transition-colors duration-300">
              {getIcon(item.type)}
              <span className="font-mono">{item.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};