import React from 'react';
import { UserPlus, Settings, Key, Wallet, ArrowRight } from 'lucide-react';

export const ProcessSteps: React.FC = () => {
  const steps = [
    {
      icon: <UserPlus className="w-6 h-6" />,
      title: "1. 启动机器人",
      desc: "在 Telegram 中打开 @PayShieldBot，点击 Start 即可自动开户，无需 KYC。"
    },
    {
      icon: <Settings className="w-6 h-6" />,
      title: "2. 绑定收款方式",
      desc: "设置您的 USDT-TRC20 结算地址，并绑定用于收款的支付宝/微信个人码。"
    },
    {
      icon: <Key className="w-6 h-6" />,
      title: "3. 获取 API 密钥",
      desc: "在商户面板生成 API Key 和 Secret，对照文档 5 分钟完成接口对接。"
    },
    {
      icon: <Wallet className="w-6 h-6" />,
      title: "4. 开始躺赚",
      desc: "用户支付法币 -> 系统秒兑 USDT -> 自动打入您的钱包。D0 实时到账。"
    }
  ];

  return (
    <section className="py-20 bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-white/5 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="text-blue-600 dark:text-brand-blue font-bold tracking-wider uppercase text-sm">How it works</span>
          <h2 className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            极简接入流程，<span className="relative inline-block">
              <span className="relative z-10">最快 10 分钟上线</span>
              <span className="absolute bottom-1 left-0 w-full h-3 bg-blue-200 dark:bg-brand-blue/30 -rotate-1"></span>
            </span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
          {/* Connector Line (Desktop only) */}
          <div className="hidden md:block absolute top-12 left-0 w-full h-0.5 bg-slate-100 dark:bg-slate-800 -z-0"></div>

          {steps.map((step, index) => (
            <div key={index} className="relative z-10 flex flex-col items-center text-center group">
              <div className="w-24 h-24 rounded-2xl bg-white dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 flex items-center justify-center mb-6 shadow-lg shadow-slate-200/50 dark:shadow-none group-hover:border-blue-500 dark:group-hover:border-brand-blue group-hover:scale-105 transition-all duration-300">
                <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center text-blue-600 dark:text-brand-blue group-hover:bg-blue-600 group-hover:text-white dark:group-hover:bg-brand-blue dark:group-hover:text-slate-900 transition-colors">
                  {step.icon}
                </div>
              </div>
              
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">{step.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed px-2">
                {step.desc}
              </p>

              {/* Mobile Arrow */}
              {index < steps.length - 1 && (
                <div className="md:hidden mt-8 text-slate-300 dark:text-slate-700">
                  <ArrowRight className="w-6 h-6 rotate-90" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};