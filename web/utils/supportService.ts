/**
 * 客服分配服务工具函数
 * 用于Web网站（5050.usdt2026.cc）的客服分配功能
 * 使用前端硬编码的10个客服账号，实现顺序轮询分配
 */

// 10个客服账号列表（硬编码，移除@符号）
const CUSTOMER_SERVICE_ACCOUNTS = [
  'zxc123456cxsj',
  'wubaizhifuaran',
  'Mark77585',
  'Moon727888',
  'yuanpay_01',
  'wushizhifu888',
  'wushi987',
  'xiaoyue5918',
  'Aeight888',
  'wuzhifu_8'
];

// localStorage key for storing current index
const ROUND_ROBIN_INDEX_KEY = 'cs_round_robin_index';

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
 * 使用顺序轮询（Round Robin）方式分配客服账号
 * @returns 分配的客服账号（不含@符号）
 */
function assignCustomerServiceRoundRobin(): string {
  try {
    // 从localStorage获取当前索引
    let currentIndex = 0;
    const storedIndex = localStorage.getItem(ROUND_ROBIN_INDEX_KEY);
    
    if (storedIndex !== null) {
      const parsedIndex = parseInt(storedIndex, 10);
      if (!isNaN(parsedIndex) && parsedIndex >= 0 && parsedIndex < CUSTOMER_SERVICE_ACCOUNTS.length) {
        currentIndex = parsedIndex;
      }
    }
    
    // 获取当前分配的账号
    const assignedAccount = CUSTOMER_SERVICE_ACCOUNTS[currentIndex];
    
    // 更新索引（循环）
    const nextIndex = (currentIndex + 1) % CUSTOMER_SERVICE_ACCOUNTS.length;
    localStorage.setItem(ROUND_ROBIN_INDEX_KEY, nextIndex.toString());
    
    console.log(`分配客服账号: @${assignedAccount} (索引: ${currentIndex} -> ${nextIndex})`);
    
    return assignedAccount;
  } catch (error) {
    console.error('Error in round robin assignment:', error);
    // 如果出错，返回第一个账号作为fallback
    return CUSTOMER_SERVICE_ACCOUNTS[0];
  }
}

/**
 * 分配客服账号（前端实现，不调用API）
 * @returns 分配结果
 */
export async function assignCustomerService(): Promise<CustomerServiceAssignmentResult> {
  try {
    // 使用顺序轮询分配
    const assignedAccount = assignCustomerServiceRoundRobin();
    
    return {
      success: true,
      service_account: assignedAccount,
      assignment_method: 'round_robin',
    };
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
