/**
 * 客服分配服务工具函数
 * 用于Web网站（5050.usdt2026.cc）的客服分配功能
 */

/**
 * 获取用户ID（支持Telegram WebApp和匿名用户）
 */
function getUserId(): number | null {
  try {
    // 优先从Telegram WebApp获取
    if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
      return window.Telegram.WebApp.initDataUnsafe.user.id;
    }
    
    // 如果不在Telegram环境中，生成临时负数ID
    const TEMP_USER_ID_KEY = 'web_temp_user_id';
    let tempUserId = sessionStorage.getItem(TEMP_USER_ID_KEY);
    
    if (!tempUserId) {
      // 生成基于时间戳的临时ID（负数）
      const timestamp = Date.now();
      tempUserId = `-${timestamp}`;
      sessionStorage.setItem(TEMP_USER_ID_KEY, tempUserId);
    }
    
    // 转换为数字（如果太大，使用hash）
    const numericId = parseInt(tempUserId);
    if (isNaN(numericId) || numericId > 0) {
      // 如果解析失败或不是负数，使用hash生成负数ID
      let hash = 0;
      for (let i = 0; i < tempUserId.length; i++) {
        const char = tempUserId.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return -Math.abs(hash); // 确保是负数
    }
    
    return numericId;
  } catch (e) {
    console.warn('Failed to get user ID:', e);
    // 生成一个随机负数ID作为fallback
    return -Math.floor(Math.random() * 1_000_000_000) - 1;
  }
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

    // 确定API URL（Web网站使用5050.usdt2026.cc的API）
    const isHttps = window.location.protocol === 'https:';
    const apiUrl = import.meta.env.VITE_API_URL || 
      (isHttps ? 'https://5050.usdt2026.cc/api' : 'http://5050.usdt2026.cc/api');
    
    // 准备请求头
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // 如果有Telegram initData，添加到请求头
    if (initData) {
      headers['X-Telegram-Init-Data'] = initData;
    }
    
    const response = await fetch(`${apiUrl}/customer-service/assign`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        user_id: userId,
        username: username,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `API call failed: ${response.status}`;
      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        errorMessage = errorText || errorMessage;
      }
      
      console.error('API error:', errorMessage);
      return {
        success: false,
        service_account: null,
        error: errorMessage,
      };
    }

    const data = await response.json();
    
    if (data.success && data.service_account) {
      return {
        success: true,
        service_account: data.service_account,
        assignment_method: data.assignment_method || 'round_robin',
      };
    } else {
      return {
        success: false,
        service_account: null,
        error: data.message || 'Failed to assign customer service',
      };
    }
  } catch (error) {
    console.error('Error assigning customer service:', error);
    return {
      success: false,
      service_account: null,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * 打开客服对话（分配客服并跳转）
 * @param fallbackUrl 如果分配失败，使用的备用URL
 */
export async function openSupportChat(fallbackUrl: string = 'https://t.me/PayShieldSupport'): Promise<void> {
  const result = await assignCustomerService();
  
  if (result.success && result.service_account) {
    // 移除@符号（如果有）
    const username = result.service_account.replace('@', '');
    window.open(`https://t.me/${username}`, '_blank');
  } else {
    // 分配失败，使用备用URL
    console.warn('Customer service assignment failed, using fallback:', result.error);
    window.open(fallbackUrl, '_blank');
  }
}
