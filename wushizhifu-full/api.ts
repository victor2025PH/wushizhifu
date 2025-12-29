/**
 * API client for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://50zf.usdt2026.cc/api';

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  language_code?: string;
}

export interface UserResponse {
  user_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  language_code?: string;
  is_premium: boolean;
  vip_level: number;
  total_transactions: number;
  total_amount: number;
  created_at: string;
  last_active_at: string;
}

export interface StatisticsResponse {
  total_transactions: number;
  total_receive: number;
  total_pay: number;
  total_amount: number;
  vip_level: number;
}

export interface TransactionResponse {
  transaction_id: number;
  order_id: string;
  transaction_type: string;
  payment_channel: string;
  amount: number;
  fee: number;
  actual_amount: number;
  currency: string;
  status: string;
  description?: string;
  created_at: string;
  paid_at?: string;
  expired_at?: string;
}

class ApiClient {
  private getInitData(): string | null {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp?.initData) {
      return window.Telegram.WebApp.initData;
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const initData = this.getInitData();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (initData) {
      headers['X-Telegram-Init-Data'] = initData;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Sync user information from Telegram to backend
   */
  async syncUser(user: TelegramUser): Promise<UserResponse> {
    const initData = this.getInitData();
    
    return this.request<UserResponse>('/auth/sync', {
      method: 'POST',
      body: JSON.stringify({
        init_data: initData || '',
        user: {
          id: user.id,
          first_name: user.first_name,
          last_name: user.last_name,
          username: user.username,
          photo_url: user.photo_url,
          language_code: user.language_code,
        },
      }),
    });
  }

  /**
   * Get current user information
   * Returns null if initData is not available (e.g., opened from ReplyKeyboard)
   */
  async getCurrentUser(): Promise<UserResponse | null> {
    // Only try if we have initData
    const initData = this.getInitData();
    if (!initData) {
      console.warn("No initData available, cannot get user from backend");
      return null;
    }
    
    try {
      return await this.request<UserResponse>('/user/me');
    } catch (error) {
      console.error("Failed to get current user:", error);
      return null;
    }
  }

  /**
   * Get user statistics
   */
  async getStatistics(): Promise<StatisticsResponse> {
    return this.request<StatisticsResponse>('/user/statistics');
  }

  /**
   * Get user transactions
   */
  async getTransactions(params?: {
    limit?: number;
    offset?: number;
    transaction_type?: string;
    status?: string;
  }): Promise<TransactionResponse[]> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.transaction_type) queryParams.append('transaction_type', params.transaction_type);
    if (params?.status) queryParams.append('status', params.status);

    const query = queryParams.toString();
    return this.request<TransactionResponse[]>(`/transactions${query ? `?${query}` : ''}`);
  }

  /**
   * Get exchange rates
   */
  async getRates(): Promise<{
    alipay: { fee_rate: number; min_amount: number; max_amount: number };
    wechat: { fee_rate: number; min_amount: number; max_amount: number };
    vip_level: number;
  }> {
    return this.request('/rates');
  }
}

export const apiClient = new ApiClient();

