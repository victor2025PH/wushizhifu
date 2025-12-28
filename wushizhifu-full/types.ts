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
    withdraw: "Withdraw",
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
    // Branding & Common
    appName: "WuShiPay",
    appTicker: "WUSHIPAY",
    premium: "Premium",
    tetherUsd: "Tether USD",
    techLtd: "WuShiPay Tech Ltd.",
    rate: "Rate",
    switchMode: "Switch",
    inputPlaceholder: "100-50000",
    // Navigation
    navHome: "Home",
    navWallet: "Wallet",
    navActivity: "Records",
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
    logout: "Disconnect",
    // About Page
    aboutTitle: "About Us",
    companyDesc: "WuShiPay is a leading digital asset payment solution provider in the Telegram ecosystem. We aggregate global top-tier payment channels to provide users with millisecond-level response and zero-loss payment experiences.",
    feature1Title: "Industry Leading Success Rate",
    feature1Desc: "Smart routing algorithm guarantees 99.9% transaction success.",
    feature2Title: "Financial Grade Security",
    feature2Desc: "Multi-signature cold storage and full compensation guarantee.",
    feature3Title: "Premium Service",
    feature3Desc: "24/7 Dedicated 1-on-1 customer support.",
    // Alipay Guide
    alipayGuideTitle: "Payment Guide",
    watchVideo: "Watch Video Tutorial",
    alipayGuideStep1: "Step 1: Confirm Order & Payment Method",
    alipayGuideStep1Desc: "Review the total amount (including product amount and system handling fee) on the payment page. The 'Alipay' (Alipay) icon is selected by default. Click the payment button at the bottom.",
    alipayGuideStep2: "Step 2: Wait for System Redirect",
    alipayGuideStep2Desc: "A prompt will appear: 'Redirecting to payment page, please wait...'. Do not close or refresh the page, wait patiently for 1-3 seconds.",
    alipayGuideStep3: "Step 3: Confirm Opening Alipay",
    alipayGuideStep3Desc: "Your phone system will show a dialog: 'Open this page in Alipay?'",
    alipayGuideStep3Important: "Important: You must click the [Open] button. If you click Cancel, payment cannot be initiated.",
    alipayGuideStep4: "Step 4: Complete Payment",
    alipayGuideStep4Desc: "The system will automatically redirect to the Alipay APP payment interface. Review the amount again, select your payment method (e.g., Balance, Bank Card, or Huabei), and click [Confirm Payment], then verify with fingerprint/face or password.",
    alipayGuideStep5: "Step 5: Payment Success",
    alipayGuideStep5Desc: "After verification, Alipay will show 'Payment Successful' page. You can click 'Done' or return to the merchant website to check order status.",
    alipayGuideTips: "Tips",
    alipayGuideTip1: "Handling Fee: The final payment amount may include a small platform handling fee, please refer to the actual amount displayed.",
    alipayGuideTip2: "Cannot Redirect: If clicking 'Open' has no response, please check if Alipay APP is installed, or try refreshing the page to initiate payment again.",
    alipayGuideConfirm: "I Understand, Continue Payment",
    cancel: "Cancel",
    // WeChat Guide
    wechatGuideTitle: "WeChat Pay Guide",
    wechatGuideStep1: "Step 1: Open WeChat App",
    wechatGuideStep1Desc: "Ensure WeChat is installed on your phone. Open the WeChat app from your home screen or app drawer.",
    wechatGuideStep2: "Step 2: Use Scan QR Code",
    wechatGuideStep2Desc: "After clicking the payment button, a QR code will appear. Open WeChat and tap on the \"+\" icon at the top right, then select \"Scan QR Code\" or \"扫一扫\".",
    wechatGuideStep3: "Step 3: Scan the Payment QR Code",
    wechatGuideStep3Desc: "Point your phone camera at the QR code displayed on the payment page. WeChat will automatically recognize the code.",
    wechatGuideStep3Important: "Important: Make sure the QR code is fully visible and well-lit for accurate scanning.",
    wechatGuideStep4: "Step 4: Confirm Payment Amount",
    wechatGuideStep4Desc: "After scanning, WeChat will display the payment details. Review the amount carefully, select your payment method (e.g., WeChat Pay Balance, Linked Bank Card), then tap \"Confirm Payment\" and verify with fingerprint/face or password.",
    wechatGuideStep5: "Step 5: Payment Success",
    wechatGuideStep5Desc: "After verification, WeChat will show a \"Payment Successful\" confirmation. You can return to the merchant page to check your order status.",
    wechatGuideTips: "Tips",
    wechatGuideTip1: "Handling Fee: The final payment amount may include a small platform handling fee, please refer to the actual amount displayed.",
    wechatGuideTip2: "Cannot Scan: If the QR code cannot be scanned, ensure your phone camera has proper permissions, try adjusting the distance or lighting, or refresh the page to generate a new QR code.",
    wechatGuideConfirm: "I Understand, Continue Payment"
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
    withdraw: "提现",
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
    // Branding & Common
    appName: "伍拾支付",
    appTicker: "WUSHIPAY",
    premium: "尊享版",
    tetherUsd: "泰达币 (USDT)",
    techLtd: "伍拾支付科技有限公司",
    rate: "汇率",
    switchMode: "切换",
    inputPlaceholder: "100-50000",
    // Navigation
    navHome: "首页",
    navWallet: "钱包",
    navActivity: "记录",
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
    about: "关于我们",
    verification: "实名认证",
    verified: "已认证",
    logout: "断开连接",
    // About Page
    aboutTitle: "关于我们",
    companyDesc: "伍拾支付 (WuShiPay) 是 Telegram 生态中领先的数字资产支付解决方案提供商。我们依托自研的“极速核心”撮合引擎，聚合全球顶尖支付通道，为用户提供毫秒级响应、零掉单的极致支付体验。您的每一笔交易，都有我们银行级的风控体系保驾护航。",
    feature1Title: "99.9% 交易成功率",
    feature1Desc: "独家智能路由算法，自动切换最优通道，确保极速到账。",
    feature2Title: "金融级资金安全",
    feature2Desc: "采用多重签名冷钱包存储技术，提供全额赔付保障，让您无后顾之忧。",
    feature3Title: "尊享级客户服务",
    feature3Desc: "7x24小时 1对1 专属客服在线，秒级响应您的任何需求。",
    // Alipay Guide
    alipayGuideTitle: "支付操作指南",
    watchVideo: "观看视频教程",
    alipayGuideStep1: "第一步：确认订单与支付方式",
    alipayGuideStep1Desc: "在收银台页面，核对合计金额（包含商品金额及系统手续费）。默认勾选\"支付宝\"(Alipay) 图标。点击底部的支付按钮。",
    alipayGuideStep2: "第二步：等待系统跳转",
    alipayGuideStep2Desc: "页面会出现提示弹窗：\"正在为您跳转到支付页面，请稍候...\"。此时请勿关闭页面或刷新，耐心等待 1-3 秒。",
    alipayGuideStep3: "第三步：确认唤起支付宝",
    alipayGuideStep3Desc: "手机系统会弹出对话框提示：\"在'支付宝'中打开此页？\"。",
    alipayGuideStep3Important: "关键操作：请务必点击【打开】按钮。注意：如果点击取消，将无法拉起支付。",
    alipayGuideStep4: "第四步：完成支付",
    alipayGuideStep4Desc: "系统将自动跳转至支付宝 APP 的收银台界面。再次核对金额，选择您的付款方式（如：余额宝、银行卡或花呗），点击底部的【确认付款】按钮，并进行指纹/面容或密码验证。",
    alipayGuideStep5: "第五步：支付成功",
    alipayGuideStep5Desc: "验证通过后，支付宝显示\"支付成功\"页面。此时可点击\"完成\"或直接返回商户网页查看订单状态。",
    alipayGuideTips: "温馨提示",
    alipayGuideTip1: "手续费说明：最终支付金额可能包含少量平台手续费，请以实际显示为准。",
    alipayGuideTip2: "无法跳转怎么办：如果点击\"打开\"后没有反应，请检查是否已安装支付宝 APP，或尝试刷新页面重新发起支付。",
    alipayGuideConfirm: "我知道了，继续支付",
    cancel: "取消",
    // WeChat Guide
    wechatGuideTitle: "微信支付操作指南",
    wechatGuideStep1: "第一步：打开微信应用",
    wechatGuideStep1Desc: "确保您的手机上已安装微信 APP。从主屏幕或应用抽屉中找到并打开微信应用。",
    wechatGuideStep2: "第二步：使用扫一扫功能",
    wechatGuideStep2Desc: "点击支付按钮后，页面会显示一个二维码。打开微信，点击右上角的 \"+\" 图标，然后选择 \"扫一扫\" 功能。",
    wechatGuideStep3: "第三步：扫描支付二维码",
    wechatGuideStep3Desc: "将手机摄像头对准支付页面上显示的二维码。微信会自动识别并读取二维码信息。",
    wechatGuideStep3Important: "关键操作：请确保二维码完整清晰，光线充足，以便准确扫描。",
    wechatGuideStep4: "第四步：确认支付金额",
    wechatGuideStep4Desc: "扫描成功后，微信会显示支付详情页面。请仔细核对金额，选择您的付款方式（如：微信零钱、绑定的银行卡），然后点击 \"确认支付\" 按钮，并进行指纹/面容或密码验证。",
    wechatGuideStep5: "第五步：支付成功",
    wechatGuideStep5Desc: "验证通过后，微信会显示 \"支付成功\" 确认页面。此时可返回商户页面查看订单状态。",
    wechatGuideTips: "温馨提示",
    wechatGuideTip1: "手续费说明：最终支付金额可能包含少量平台手续费，请以实际显示为准。",
    wechatGuideTip2: "无法扫描怎么办：如果二维码无法扫描，请检查手机摄像头权限是否开启，尝试调整距离或光线，或刷新页面重新生成二维码。",
    wechatGuideConfirm: "我知道了，继续支付"
  }
};