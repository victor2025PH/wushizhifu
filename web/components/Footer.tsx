import React from 'react';
import { ShieldCheck, Send } from 'lucide-react';
import { PageView } from '../App';

interface FooterProps {
  onNavigate: (page: PageView) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="bg-slate-100 dark:bg-slate-950 border-t border-slate-200 dark:border-white/10 pt-16 pb-8 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-4 cursor-pointer" onClick={() => onNavigate('home')}>
              <ShieldCheck className="h-6 w-6 text-blue-600 dark:text-brand-blue" />
              <span className="text-xl font-bold text-slate-900 dark:text-white">伍拾支付</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 max-w-sm mb-6">
              专为高并发业务设计的 Telegram 支付网关。保护您的现金流，让支付更安全、更私密、更高效。
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-white transition-colors">
                <Send className="w-5 h-5" />
              </a>
            </div>
          </div>
          
          <div>
            <h4 className="text-slate-900 dark:text-white font-bold mb-4">产品</h4>
            <ul className="space-y-2">
              <li>
                <button onClick={() => { onNavigate('home'); setTimeout(() => document.getElementById('features')?.scrollIntoView({behavior: 'smooth'}), 100); }} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  功能介绍
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('fees')} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  费率说明
                </button>
              </li>
              <li>
                <button onClick={() => { onNavigate('home'); setTimeout(() => document.getElementById('api')?.scrollIntoView({behavior: 'smooth'}), 100); }} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  API 文档
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('changelog')} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  更新日志
                </button>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-slate-900 dark:text-white font-bold mb-4">法律与支持</h4>
            <ul className="space-y-2">
              <li>
                <button onClick={() => onNavigate('privacy')} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  隐私政策
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('terms')} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  服务条款
                </button>
              </li>
              <li>
                <button onClick={() => document.querySelector('[aria-label="联系客服"]')?.dispatchEvent(new MouseEvent('click', { bubbles: true }))} className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-brand-blue text-sm transition-colors">
                  联系客服
                </button>
              </li>
            </ul>
          </div>

        </div>
        
        <div className="border-t border-slate-200 dark:border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-500 text-sm">© 2024 PayShield Tech. All rights reserved.</p>
          <div className="text-slate-500 dark:text-slate-600 text-xs">
            系统版本 v1.2.0 | 节点状态: 正常
          </div>
        </div>
      </div>
    </footer>
  );
};