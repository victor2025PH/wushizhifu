import React from 'react';
import { Send, LayoutDashboard, Activity } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <div className="relative pt-32 pb-12 sm:pt-40 sm:pb-16 overflow-hidden bg-slate-50 dark:bg-transparent transition-colors duration-300">
      {/* Background gradients for Dark Mode */}
      <div className="hidden dark:block absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl pointer-events-none">
        <div className="absolute top-20 left-1/4 w-72 h-72 bg-brand-blue/20 rounded-full blur-[100px] mix-blend-screen animate-pulse"></div>
        <div className="absolute top-40 right-1/4 w-96 h-96 bg-brand-purple/20 rounded-full blur-[100px] mix-blend-screen"></div>
      </div>
      
      {/* Background grid for Light Mode */}
      <div className="dark:hidden absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10">
        <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-white border border-slate-200 shadow-sm dark:bg-white/5 dark:border-white/10 dark:shadow-none mb-8 backdrop-blur-sm transition-all group cursor-pointer hover:border-blue-400 dark:hover:border-brand-blue/50">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 dark:bg-brand-blue opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-600 dark:bg-brand-blue"></span>
          </span>
          <span className="font-mono text-sm text-slate-600 dark:text-slate-300">
            <span className="font-bold text-slate-900 dark:text-white">Live:</span> USDT 实时结算中
          </span>
          <span className="h-4 w-px bg-slate-300 dark:bg-white/20"></span>
          <span className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
            <Activity className="w-3 h-3" />
            Avg. 1.2s
          </span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6 leading-tight">
          告别账户冻结风险 <br />
          <span className="text-blue-600 dark:text-transparent dark:bg-clip-text dark:bg-gradient-to-r dark:from-brand-blue dark:to-brand-purple">
            大额交易首选的安全支付网关
          </span>
        </h1>

        <p className="mt-4 max-w-3xl mx-auto text-xl text-slate-600 dark:text-slate-400 mb-10 leading-relaxed">
          专为高并发业务打造。集成 Telegram，自动投诉拦截，<span className="font-semibold text-slate-900 dark:text-white">D0 级 USDT 秒结算</span>。
          <br className="hidden sm:block" />
          保护您的现金流，让每一笔收款都安全落地。
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
          <a
            href="https://t.me/PayShieldBot"
            target="_blank"
            rel="noreferrer"
            className="group flex items-center justify-center gap-2 bg-blue-600 text-white dark:bg-brand-blue dark:text-slate-950 px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-700 dark:hover:bg-cyan-300 transition-all shadow-lg shadow-blue-600/20 dark:shadow-[0_0_20px_rgba(0,240,255,0.3)] transform hover:-translate-y-1"
          >
            <Send className="w-5 h-5 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition-transform" />
            启动机器人
          </a>
          
          <a
            href="https://t.me/PayShieldBot/app"
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-center gap-2 bg-white text-slate-700 border border-slate-200 dark:bg-white/5 dark:text-white dark:border-white/10 px-8 py-4 rounded-xl text-lg font-bold hover:bg-slate-50 dark:hover:bg-white/10 transition-all backdrop-blur-md shadow-sm dark:shadow-none"
          >
            <LayoutDashboard className="w-5 h-5" />
            打开 WebApp
          </a>
        </div>

        {/* Trust Stats Badge Section */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 md:gap-12 max-w-4xl mx-auto mb-16 px-4">
          <div className="flex flex-col items-center justify-center relative">
            <span className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white mb-1 tracking-tight tabular-nums">
              $10M<span className="text-blue-600 dark:text-brand-blue text-2xl md:text-3xl align-top">+</span>
            </span>
            <span className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">累计安全结算</span>
          </div>
          
          <div className="flex flex-col items-center justify-center relative">
            {/* Divider lines for desktop */}
            <div className="hidden md:block absolute left-0 top-1/2 -translate-y-1/2 w-px h-8 bg-slate-200 dark:bg-white/10"></div>
            <div className="hidden md:block absolute right-0 top-1/2 -translate-y-1/2 w-px h-8 bg-slate-200 dark:bg-white/10"></div>
            
            <span className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white mb-1 tracking-tight tabular-nums">
              5000<span className="text-purple-600 dark:text-brand-purple text-2xl md:text-3xl align-top">+</span>
            </span>
            <span className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">商户信赖之选</span>
          </div>

          <div className="col-span-2 md:col-span-1 flex flex-col items-center justify-center relative">
            <span className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white mb-1 tracking-tight tabular-nums">
              0<span className="text-green-500 text-base md:text-xl align-middle ml-1">起</span>
            </span>
            <span className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">资金冻结事故</span>
          </div>
        </div>

        {/* Trust Indicators / Supported Networks */}
        <div className="border-t border-slate-200 dark:border-white/5 pt-8">
            <p className="text-sm text-slate-500 dark:text-slate-500 mb-6 font-medium uppercase tracking-wider">安全支持以下网络与协议</p>
            <div className="flex flex-wrap justify-center gap-6 sm:gap-12 opacity-70 grayscale hover:grayscale-0 transition-all duration-500">
                {/* Simulated Logos with Text for simplicity and reliability */}
                <div className="flex items-center gap-2 group cursor-default">
                    <div className="w-8 h-8 rounded-full bg-[#26A17B] flex items-center justify-center text-white font-bold text-xs shadow-lg shadow-[#26A17B]/20 group-hover:scale-110 transition-transform">T</div>
                    <span className="font-bold text-slate-700 dark:text-white group-hover:text-[#26A17B] transition-colors">Tether (TRC20)</span>
                </div>
                <div className="flex items-center gap-2 group cursor-default">
                    <div className="w-8 h-8 rounded-full bg-[#00D188] flex items-center justify-center text-white font-bold text-xs shadow-lg shadow-[#00D188]/20 group-hover:scale-110 transition-transform">W</div>
                    <span className="font-bold text-slate-700 dark:text-white group-hover:text-[#00D188] transition-colors">WeChat Pay</span>
                </div>
                <div className="flex items-center gap-2 group cursor-default">
                    <div className="w-8 h-8 rounded-full bg-[#1677FF] flex items-center justify-center text-white font-bold text-xs shadow-lg shadow-[#1677FF]/20 group-hover:scale-110 transition-transform">A</div>
                    <span className="font-bold text-slate-700 dark:text-white group-hover:text-[#1677FF] transition-colors">Alipay</span>
                </div>
                <div className="flex items-center gap-2 group cursor-default">
                    <div className="w-8 h-8 rounded-full bg-[#0088CC] flex items-center justify-center text-white font-bold text-xs shadow-lg shadow-[#0088CC]/20 group-hover:scale-110 transition-transform">TG</div>
                    <span className="font-bold text-slate-700 dark:text-white group-hover:text-[#0088CC] transition-colors">Telegram Bot</span>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};