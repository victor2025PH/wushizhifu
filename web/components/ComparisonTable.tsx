import React from 'react';
import { Check, X, Minus } from 'lucide-react';

export const ComparisonTable: React.FC = () => {
  return (
    <section className="py-24 bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
            为什么顶级商户都在用 <span className="text-blue-600 dark:text-brand-blue">伍拾支付</span>？
          </h2>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            拒绝套路，用实力说话。全方位对比传统支付通道与易支付平台。
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl shadow-xl dark:shadow-none border border-slate-200 dark:border-white/10">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-700 uppercase bg-slate-100 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th scope="col" className="px-6 py-5 text-base font-bold w-1/4">功能指标</th>
                <th scope="col" className="px-6 py-5 text-base font-bold w-1/4 bg-blue-50 dark:bg-brand-blue/10 text-blue-700 dark:text-brand-blue border-b-2 border-blue-500 dark:border-brand-blue">
                  伍拾支付 (PayShield)
                </th>
                <th scope="col" className="px-6 py-5 text-base font-bold w-1/4 text-slate-500 dark:text-slate-400">
                  传统三方支付
                </th>
                <th scope="col" className="px-6 py-5 text-base font-bold w-1/4 text-slate-500 dark:text-slate-400">
                  个人码挂机
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700 bg-white dark:bg-slate-900/50">
              {/* Row 1 */}
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                <th scope="row" className="px-6 py-4 font-medium text-slate-900 dark:text-white whitespace-nowrap">
                  结算速度
                </th>
                <td className="px-6 py-4 bg-blue-50/30 dark:bg-brand-blue/5 font-bold text-green-600 dark:text-green-400">
                  D0 秒级 (USDT)
                </td>
                <td className="px-6 py-4 text-slate-500">
                  T+1 / T+7
                </td>
                <td className="px-6 py-4 text-slate-500">
                  即时 (但风险极高)
                </td>
              </tr>
              {/* Row 2 */}
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                <th scope="row" className="px-6 py-4 font-medium text-slate-900 dark:text-white">
                  抗投诉/防冻结
                </th>
                <td className="px-6 py-4 bg-blue-50/30 dark:bg-brand-blue/5">
                  <div className="flex items-center gap-2 text-slate-900 dark:text-white">
                    <Check className="w-5 h-5 text-green-500" />
                    <span>自动退款熔断机制</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-slate-500">
                    <X className="w-5 h-5 text-red-400" />
                    <span>无 (一封全死)</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-slate-500">
                     <X className="w-5 h-5 text-red-400" />
                    <span>极易冻结</span>
                  </div>
                </td>
              </tr>
              {/* Row 3 */}
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                <th scope="row" className="px-6 py-4 font-medium text-slate-900 dark:text-white">
                  隐私保护
                </th>
                <td className="px-6 py-4 bg-blue-50/30 dark:bg-brand-blue/5">
                  <div className="flex items-center gap-2 text-slate-900 dark:text-white">
                    <Check className="w-5 h-5 text-green-500" />
                    <span>Telegram 端到端加密</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-slate-500">
                    <Minus className="w-5 h-5" />
                    <span>需实名/KYC</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                   <div className="flex items-center gap-2 text-slate-500">
                    <Minus className="w-5 h-5" />
                    <span>完全暴露</span>
                  </div>
                </td>
              </tr>
               {/* Row 4 */}
               <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                <th scope="row" className="px-6 py-4 font-medium text-slate-900 dark:text-white">
                  开户费用
                </th>
                <td className="px-6 py-4 bg-blue-50/30 dark:bg-brand-blue/5 font-bold text-slate-900 dark:text-white">
                  0 元 (仅收手续费)
                </td>
                <td className="px-6 py-4 text-slate-500">
                  几千至数万元
                </td>
                <td className="px-6 py-4 text-slate-500">
                   免费
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div className="mt-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
                * 数据基于平台过去 30 天平均交易统计
            </p>
        </div>
      </div>
    </section>
  );
};