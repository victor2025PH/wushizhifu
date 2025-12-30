/**
 * 客服服务工具
 * 支持多个客服账号轮询分配
 */

// 客服账号列表（可以扩展）
const SUPPORT_ACCOUNTS = [
  'wushizhifu_jianglai', // 第一个客服账号
  // 后续可以添加更多账号，例如：
  // 'wushizhifu_support2',
  // 'wushizhifu_support3',
];

/**
 * 获取客服账号（轮询方式）
 * @returns 选中的客服账号用户名（不含 @）
 */
export function getSupportAccount(): string {
  if (SUPPORT_ACCOUNTS.length === 0) {
    // 如果没有配置客服账号，返回默认账号
    return 'wushizhifu_jianglai';
  }

  // 简单的轮询：随机选择一个账号
  // 后续可以改为更智能的分配策略（如：按负载、按在线状态等）
  const randomIndex = Math.floor(Math.random() * SUPPORT_ACCOUNTS.length);
  return SUPPORT_ACCOUNTS[randomIndex];
}

/**
 * 打开 Telegram 客服对话
 * @param account 客服账号用户名（可选，不传则自动选择）
 */
export function openSupportChat(account?: string): void {
  const supportAccount = account || getSupportAccount();
  const supportUrl = `https://t.me/${supportAccount}`;

  // 优先使用 Telegram WebApp API
  if (window.Telegram?.WebApp?.openLink) {
    window.Telegram.WebApp.openLink(supportUrl);
  } else if (window.Telegram?.WebApp?.openTelegramLink) {
    // 备用方案：使用 openTelegramLink（如果可用）
    window.Telegram.WebApp.openTelegramLink(supportUrl);
  } else {
    // 降级方案：在新窗口打开
    window.open(supportUrl, '_blank');
  }
}

/**
 * 添加客服账号到轮询列表
 * @param account 客服账号用户名（不含 @）
 */
export function addSupportAccount(account: string): void {
  if (!SUPPORT_ACCOUNTS.includes(account)) {
    SUPPORT_ACCOUNTS.push(account);
  }
}

/**
 * 移除客服账号
 * @param account 客服账号用户名（不含 @）
 */
export function removeSupportAccount(account: string): void {
  const index = SUPPORT_ACCOUNTS.indexOf(account);
  if (index > -1) {
    SUPPORT_ACCOUNTS.splice(index, 1);
  }
}

/**
 * 获取所有客服账号列表
 * @returns 客服账号数组
 */
export function getAllSupportAccounts(): string[] {
  return [...SUPPORT_ACCOUNTS];
}

