export type ViewState = 'loading' | 'dashboard' | 'wallet' | 'history' | 'profile' | 'payment' | 'result';

export type PaymentProvider = 'alipay' | 'wechat';

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  language_code?: string;
}

export interface Transaction {
  id: string;
  type: 'topup' | 'withdraw';
  amount: number;
  currency: 'USDT' | 'CNY';
  status: 'success' | 'pending' | 'failed';
  date: string;
  provider?: PaymentProvider;
}

export interface AppState {
  view: ViewState;
  provider: PaymentProvider | null;
  amount: number;
}

export const EXCHANGE_RATE_CNY_USDT = 7.24; // Mock live rate

export type Language = 'en' | 'zh';

export const TRANSLATIONS = {
  en: {
    loading: "Initializing Secure Core",
    totalAssets: "Total Assets",
    exchangeRate: "Exchange Rate",
    cnyToUsdt: "CNY to USDT",
    liveUpdate: "Live Update",
    selectChannel: "Select Channel",
    instant: "Instant",
    fastSecure: "Fast & Secure",
    verifiedMerchant: "Verified Merchant",
    secureGateway: "WuShiPay Secure Gateway",
    topUp: "Top Up",
    via: "via",
    enterAmount: "Enter Amount (CNY)",
    estimatedReceipt: "Estimated Receipt",
    currentRate: "Current Rate",
    generateLink: "Generate Secure Link",
    orderCreated: "Order Created",
    orderDesc: "Your payment channel has been reserved. Please complete the transaction.",
    amountToPay: "Amount to Pay",
    channel: "Channel",
    orderId: "Order ID",
    openApp: "Open {app} App",
    secureFooter: "Secure connection established. If the app does not open automatically, please contact support.",
    alipay: "Alipay",
    wechat: "WeChat Pay",
    welcome: "Welcome Back",
    guest: "Guest",
    calculator: "Calculator",
    history: "History",
    recentTransactions: "Recent Transactions",
    success: "Success",
    pending: "Pending",
    failed: "Failed",
    close: "Close",
    calculate: "Calculate",
    result: "Result",
    welcomeMessage: "Experience the premium payment gateway on Telegram.",
    getStarted: "Get Started",
    // Navigation
    navHome: "Home",
    navWallet: "Wallet",
    navActivity: "Activity",
    navProfile: "Profile",
    // Wallet
    myAssets: "My Assets",
    depositAddress: "Deposit Address",
    network: "Network",
    securityLevel: "Security Level",
    high: "High",
    receive: "Receive",
    send: "Send",
    swap: "Swap",
    // Profile
    settings: "Settings",
    language: "Language",
    support: "Support",
    about: "About",
    verification: "Verification",
    verified: "Verified",
    logout: "Disconnect"
  },
  zh: {
    loading: "正在初始化安全核心",
    totalAssets: "总资产",
    exchangeRate: "实时汇率",
    cnyToUsdt: "CNY 兑换 USDT",
    liveUpdate: "实时更新",
    selectChannel: "选择支付通道",
    instant: "极速到账",
    fastSecure: "快速 & 安全",
    verifiedMerchant: "官方认证商户",
    secureGateway: "WuShiPay 安全支付网关",
    topUp: "账户充值",
    via: "通过",
    enterAmount: "输入金额 (CNY)",
    estimatedReceipt: "预计到账",
    currentRate: "当前汇率",
    generateLink: "生成安全链接",
    orderCreated: "订单已创建",
    orderDesc: "您的支付通道已预留，请尽快完成支付。",
    amountToPay: "待支付金额",
    channel: "支付方式",
    orderId: "订单编号",
    openApp: "打开 {app}",
    secureFooter: "安全连接已建立。如未自动跳转，请联系客服。",
    alipay: "支付宝",
    wechat: "微信支付",
    welcome: "欢迎回来",
    guest: "游客",
    calculator: "汇率计算",
    history: "交易记录",
    recentTransactions: "最近交易",
    success: "成功",
    pending: "处理中",
    failed: "失败",
    close: "关闭",
    calculate: "计算",
    result: "结果",
    welcomeMessage: "体验 Telegram 上最高端的支付网关。",
    getStarted: "开始使用",
    // Navigation
    navHome: "首页",
    navWallet: "钱包",
    navActivity: "活动",
    navProfile: "我的",
    // Wallet
    myAssets: "我的资产",
    depositAddress: "充值地址",
    network: "网络",
    securityLevel: "安全等级",
    high: "高",
    receive: "接收",
    send: "发送",
    swap: "兑换",
    // Profile
    settings: "设置",
    language: "语言",
    support: "客服支持",
    about: "关于",
    verification: "实名认证",
    verified: "已认证",
    logout: "断开连接"
  }
};