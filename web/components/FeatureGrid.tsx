import React from 'react';
import { ShieldCheck, Zap, MessageSquare } from 'lucide-react';
import { FeatureProps } from '../types';

const features: FeatureProps[] = [
  {
    icon: <ShieldCheck className="w-8 h-8 text-blue-600 dark:text-brand-blue" />,
    title: "智能投诉防御系统",
    description: "独家风控算法，自动识别并退款高风险投诉订单。保护您的个人收款码（微信/支付宝）免受红码风控，确保持久稳定收款。"
  },
  {
    icon: <Zap className="w-8 h-8 text-purple-600 dark:text-brand-purple" />,
    title: "USDT D0 极速结算",
    description: "告别 T+1 或 T+7。资金 T+0 实时结算，法币收入自动兑换为 USDT，彻底隔离资金链路，保障资金安全，随用随取。"
  },
  {
    icon: <MessageSquare className="w-8 h-8 text-pink-500 dark:text-pink-500" />,
    title: "Telegram 原生体验",
    description: "无需下载额外 App，直接在 TG 机器人内管理订单、查看报表、发起提现。支持 Web App 面板，操作丝滑流畅。"
  }
];

export const FeatureGrid: React.FC = () => {
  return (
    <section id="features" className="py-24 bg-slate-50 dark:bg-slate-950 relative transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">为什么选择伍拾支付?</h2>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            我们不仅仅是支付通道，更是您的资金安全盾牌。
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="group p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/5 hover:border-blue-300 dark:hover:border-brand-blue/30 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/5 dark:hover:shadow-[0_0_30px_rgba(0,240,255,0.05)] hover:-translate-y-1"
            >
              <div className="mb-6 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 w-fit group-hover:bg-blue-50 dark:group-hover:bg-slate-800/80 transition-colors">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{feature.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};