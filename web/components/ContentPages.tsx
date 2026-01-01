import React, { useEffect } from 'react';
import { ChevronLeft, FileText, Shield, Clock, CreditCard } from 'lucide-react';

interface PageProps {
  onBack: () => void;
}

// Common Wrapper for consistent layout
const PageWrapper: React.FC<{ children: React.ReactNode; title: string; subtitle?: string; onBack: () => void }> = ({ children, title, subtitle, onBack }) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="pt-24 pb-16 min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <button 
          onClick={onBack}
          className="group flex items-center gap-2 text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-brand-blue mb-8 transition-colors"
        >
          <div className="p-1 rounded-full bg-slate-100 dark:bg-slate-800 group-hover:bg-blue-50 dark:group-hover:bg-slate-700 transition-colors">
            <ChevronLeft className="w-5 h-5" />
          </div>
          <span className="font-medium">返回首页</span>
        </button>

        <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 sm:p-12 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-200 dark:border-white/5">
          <div className="mb-10 border-b border-slate-100 dark:border-white/5 pb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 dark:text-white mb-3">{title}</h1>
            {subtitle && <p className="text-lg text-slate-500 dark:text-slate-400">{subtitle}</p>}
          </div>
          <div className="prose prose-slate dark:prose-invert max-w-none">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export const FeesPage: React.FC<PageProps> = ({ onBack }) => (
  <PageWrapper title="费率说明" subtitle="透明、简单、无隐藏费用的价格体系" onBack={onBack}>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 not-prose mb-12">
      <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-white/5">
        <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-brand-blue/20 flex items-center justify-center text-blue-600 dark:text-brand-blue mb-4">
          <CreditCard className="w-6 h-6" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">交易手续费</h3>
        <div className="text-3xl font-black text-slate-900 dark:text-white mb-4">1.8% <span className="text-sm font-normal text-slate-500">/ 笔</span></div>
        <ul className="space-y-2 text-slate-600 dark:text-slate-400 text-sm">
          <li>• 成功交易才收费，失败不计费</li>
          <li>• 支持微信/支付宝全通道</li>
          <li>• 大额流水（月$100k+）可申请 1.2% 优惠费率</li>
        </ul>
      </div>

      <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-white/5">
        <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-brand-purple/20 flex items-center justify-center text-purple-600 dark:text-brand-purple mb-4">
          <Clock className="w-6 h-6" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">结算费用</h3>
        <div className="text-3xl font-black text-slate-900 dark:text-white mb-4">1 USDT <span className="text-sm font-normal text-slate-500">/ 笔</span></div>
        <ul className="space-y-2 text-slate-600 dark:text-slate-400 text-sm">
          <li>• D0 实时自动结算</li>
          <li>• 单笔最低结算金额 10 USDT</li>
          <li>• TRC20 链上转账矿工费（Gas）实报实销</li>
        </ul>
      </div>
    </div>
    
    <h3>常见费用问答</h3>
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-bold text-slate-900 dark:text-white">需要缴纳开户费或保证金吗？</h4>
        <p className="text-slate-600 dark:text-slate-400">不需要。伍拾支付目前处于公测推广期，免除所有开户费、年费及保证金。您只需通过 Telegram 机器人即可免费开通商户账户。</p>
      </div>
      <div>
        <h4 className="text-lg font-bold text-slate-900 dark:text-white">汇率是如何计算的？</h4>
        <p className="text-slate-600 dark:text-slate-400">我们参考 Binance 与 OKX 的 USDT/CNY 实时场外交易价格（OTC），确保汇率公正透明。系统会自动在每一笔订单中锁定汇率，避免波动风险。</p>
      </div>
    </div>
  </PageWrapper>
);

export const UpdateLogPage: React.FC<PageProps> = ({ onBack }) => (
  <PageWrapper title="更新日志" subtitle="PayShield 平台功能迭代记录" onBack={onBack}>
    <div className="relative border-l border-slate-200 dark:border-white/10 ml-3 space-y-12 not-prose">
      
      {/* v1.2.0 */}
      <div className="relative pl-8">
        <div className="absolute -left-1.5 top-1.5 w-3 h-3 bg-blue-600 dark:bg-brand-blue rounded-full ring-4 ring-white dark:ring-slate-900"></div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">v1.2.0 - 性能升级</h3>
          <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400 w-fit">Current</span>
          <span className="text-sm text-slate-500">2024-03-20</span>
        </div>
        <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-1">
          <li>新增 WebApp 商户管理面板，支持手机端查看报表。</li>
          <li>优化结算逻辑，USDT 到账速度提升 30%。</li>
          <li>修复了部分安卓设备在 Telegram 内唤起支付偶尔卡顿的问题。</li>
        </ul>
      </div>

      {/* v1.1.0 */}
      <div className="relative pl-8">
        <div className="absolute -left-1.5 top-1.5 w-3 h-3 bg-slate-300 dark:bg-slate-700 rounded-full ring-4 ring-white dark:ring-slate-900"></div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">v1.1.0 - 通道扩容</h3>
          <span className="text-sm text-slate-500">2024-02-15</span>
        </div>
        <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-1">
          <li>正式上线“熔断防御”系统，自动识别恶意投诉订单。</li>
          <li>新增支付宝 H5 唤起支持，转化率提升 15%。</li>
          <li>开放 API 接口文档，支持 Python/Node.js/PHP SDK。</li>
        </ul>
      </div>

      {/* v1.0.0 */}
      <div className="relative pl-8">
        <div className="absolute -left-1.5 top-1.5 w-3 h-3 bg-slate-300 dark:bg-slate-700 rounded-full ring-4 ring-white dark:ring-slate-900"></div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">v1.0.0 - 全球公测</h3>
          <span className="text-sm text-slate-500">2024-01-01</span>
        </div>
        <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-1">
          <li>PayShield 伍拾支付正式上线。</li>
          <li>集成 Telegram Bot 账户体系。</li>
          <li>支持 USDT-TRC20 自动结算。</li>
        </ul>
      </div>

    </div>
  </PageWrapper>
);

export const PrivacyPolicyPage: React.FC<PageProps> = ({ onBack }) => (
  <PageWrapper title="隐私政策" subtitle="生效日期：2024年1月1日" onBack={onBack}>
    <div className="text-slate-600 dark:text-slate-300 space-y-6">
      <p>
        伍拾支付（以下简称“我们”）非常重视您的隐私。本隐私政策说明了我们如何收集、使用和保护您的信息。
      </p>
      
      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">1. 信息收集</h3>
      <p>为了提供服务，我们仅收集最必要的信息：</p>
      <ul className="list-disc pl-5 space-y-2">
        <li><strong>Telegram 账户信息</strong>：用于身份验证和账户绑定。</li>
        <li><strong>交易数据</strong>：商户订单号、金额、支付状态，用于处理支付和结算。</li>
        <li><strong>钱包地址</strong>：您提供的 USDT 收款地址，用于资金结算。</li>
      </ul>
      <p>我们<strong>不会</strong>收集您的银行卡号、支付密码或任何与支付无关的个人敏感身份信息（KYC）。</p>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">2. 数据使用</h3>
      <p>我们收集的数据仅用于：</p>
      <ul className="list-disc pl-5 space-y-2">
        <li>处理您的支付订单和资金结算。</li>
        <li>防范欺诈、洗钱和其他非法活动（风控系统）。</li>
        <li>发送必要的服务通知（如结算到账提醒）。</li>
      </ul>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">3. 数据安全</h3>
      <p>我们采用业界领先的加密技术（如 AES-256 和 TLS 1.3）保护数据传输和存储的安全。您的 API 密钥在数据库中经过哈希处理，员工无法查看明文。</p>
    </div>
  </PageWrapper>
);

export const TermsPage: React.FC<PageProps> = ({ onBack }) => (
  <PageWrapper title="服务条款" subtitle="使用前请仔细阅读" onBack={onBack}>
    <div className="text-slate-600 dark:text-slate-300 space-y-6">
      <p>欢迎使用伍拾支付。通过访问或使用我们的服务，即表示您同意受本条款的约束。</p>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">1. 禁止的业务</h3>
      <p>严禁使用伍拾支付用于以下类别的交易。一旦发现，我们将立即冻结账户并停止结算：</p>
      <ul className="list-disc pl-5 space-y-2 text-red-600 dark:text-red-400 font-medium">
        <li>毒品、武器、人口贩卖等严重违法犯罪活动。</li>
        <li>恐怖主义融资。</li>
        <li>针对弱势群体的欺诈或杀猪盘。</li>
        <li>未经授权的非法集资或庞氏骗局。</li>
      </ul>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">2. 商户责任</h3>
      <p>商户有义务确保其发起的每一笔交易均基于真实的商业背景。商户应自行处理与其用户的消费纠纷。因商户业务违规导致的法律风险，由商户自行承担。</p>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">3. 免责声明</h3>
      <p>伍拾支付仅提供技术接口服务。对于因区块链网络拥堵、第三方支付渠道（微信/支付宝）故障或不可抗力导致的服务中断，我们不承担赔偿责任，但会尽力协助解决。</p>

      <h3 className="text-xl font-bold text-slate-900 dark:text-white mt-8">4. 账户终止</h3>
      <p>如果我们有理由相信您违反了本条款，我们保留随时终止您访问服务的权利。</p>
    </div>
  </PageWrapper>
);