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
 * 获取用户 ID（从 Telegram WebApp）
 * @returns 用户 ID 或 null
 */
function getUserId(): number | null {
  try {
    if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
      return window.Telegram.WebApp.initDataUnsafe.user.id;
    }
    // Try to parse from initData if available
    if (window.Telegram?.WebApp?.initData) {
      const params = new URLSearchParams(window.Telegram.WebApp.initData);
      const userParam = params.get('user');
      if (userParam) {
        try {
          const user = JSON.parse(decodeURIComponent(userParam));
          return user.id || null;
        } catch (e) {
          console.warn('Failed to parse user from initData:', e);
        }
      }
    }
  } catch (e) {
    console.warn('Failed to get user ID:', e);
  }
  return null;
}

/**
 * 客服分配结果接口
 */
export interface CustomerServiceAssignmentResult {
  success: boolean;
  service_account: string | null;
  assignment_method?: string;
  error?: string;
}

/**
 * 分配客服账号（通过 API）
 * @returns 分配结果
 */
export async function assignCustomerService(): Promise<CustomerServiceAssignmentResult> {
  try {
    const userId = getUserId();
    const username = window.Telegram?.WebApp?.initDataUnsafe?.user?.username || undefined;
    const initData = window.Telegram?.WebApp?.initData || '';

    // Call backend API to assign customer service
    const apiUrl = import.meta.env.VITE_API_URL || 'https://api.50zf.usdt2026.cc';
    
    // Prepare headers with authentication if available
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Add Telegram initData header for authentication (if available)
    if (initData) {
      headers['X-Telegram-Init-Data'] = initData;
    }
    
    const response = await fetch(`${apiUrl}/api/customer-service/assign`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        user_id: userId,
        username: username,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.success && data.service_account) {
        return {
          success: true,
          service_account: data.service_account,
          assignment_method: data.assignment_method
        };
      } else {
        return {
          success: false,
          service_account: null,
          error: '当前没有可用的客服账号，请联系管理员：@wushizhifu_jianglai'
        };
      }
    } else {
      return {
        success: false,
        service_account: null,
        error: '客服分配失败，请联系管理员：@wushizhifu_jianglai'
      };
    }
  } catch (error) {
    console.error('Error calling customer service API:', error);
    return {
      success: false,
      service_account: null,
      error: '客服分配失败，请联系管理员：@wushizhifu_jianglai'
    };
  }
}

/**
 * 打开 Telegram 客服对话
 * @param account 客服账号用户名（可选，不传则通过 API 自动分配）
 * @param onAssignmentResult 分配结果回调（可选，用于显示提示）
 */
export async function openSupportChat(
  account?: string,
  onAssignmentResult?: (result: CustomerServiceAssignmentResult) => void
): Promise<void> {
  // If account is provided, use it directly
  if (account) {
    const supportUrl = `https://t.me/${account}`;
    openTelegramLink(supportUrl);
    return;
  }

  // Otherwise, call API to get assigned customer service
  const result = await assignCustomerService();
  
  // If callback is provided, call it with the result (for showing modal)
  if (onAssignmentResult) {
    onAssignmentResult(result);
    return;
  }

  // If no callback, use old behavior (direct jump with fallback)
  if (result.success && result.service_account) {
    const supportUrl = `https://t.me/${result.service_account}`;
    openTelegramLink(supportUrl);
    console.log(`Assigned customer service: @${result.service_account} (method: ${result.assignment_method})`);
  } else {
    // Fallback to default account
    console.warn('API call failed or no account assigned, using fallback');
    const fallbackAccount = getSupportAccount();
    const supportUrl = `https://t.me/${fallbackAccount}`;
    openTelegramLink(supportUrl);
  }
}

/**
 * 打开 Telegram 链接（辅助函数）
 * @param url Telegram URL
 */
function openTelegramLink(url: string): void {
  // 优先使用 Telegram WebApp API
  if (window.Telegram?.WebApp?.openLink) {
    window.Telegram.WebApp.openLink(url);
  } else if (window.Telegram?.WebApp?.openTelegramLink) {
    // 备用方案：使用 openTelegramLink（如果可用）
    window.Telegram.WebApp.openTelegramLink(url);
  } else {
    // 降级方案：在新窗口打开
    window.open(url, '_blank');
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

