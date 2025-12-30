import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, ChevronLeft, ChevronRight, RefreshCw, Zap } from 'lucide-react';
import { Language, TRANSLATIONS } from '../types';
import { apiClient } from '../api';

interface BinanceRateModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
}

interface Merchant {
  rank: number;
  price: number;
  min_amount: number;
  max_amount: number;
  merchant_name: string;
  trade_count: number;
  finish_rate: number;
}

interface P2PData {
  merchants: Merchant[];
  payment_method: string;
  payment_label: string;
  total: number;
  page: number;
  market_stats: {
    min_price: number;
    max_price: number;
    avg_price: number;
    total_trades: number;
    merchant_count: number;
  };
}

const RANK_EMOJIS = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'];

export const BinanceRateModal: React.FC<BinanceRateModalProps> = ({
  isOpen,
  onClose,
  lang
}) => {
  const [data, setData] = useState<P2PData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'alipay' | 'wechat' | 'bank'>('alipay');
  const [page, setPage] = useState(1);
  const [refreshing, setRefreshing] = useState(false);

  const t = TRANSLATIONS[lang];
  const rowsPerPage = 10;
  const totalPages = data ? Math.ceil(data.total / rowsPerPage) : 1;

  const fetchData = async (method: string, pageNum: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.getBinanceP2P({
        payment_method: method,
        rows: rowsPerPage,
        page: pageNum
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
      console.error('Error fetching Binance P2P data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchData(paymentMethod, page);
    }
  }, [isOpen, paymentMethod, page]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData(paymentMethod, page);
  };

  const handlePaymentMethodChange = (method: 'alipay' | 'wechat' | 'bank') => {
    setPaymentMethod(method);
    setPage(1);
  };

  const formatAmount = (amount: number): string => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(0)}K`;
    }
    return amount.toFixed(0);
  };

  const getRankEmoji = (rank: number): string => {
    if (rank <= RANK_EMOJIS.length) {
      return RANK_EMOJIS[rank - 1];
    }
    return `${rank}.`;
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden pointer-events-auto flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-100 bg-gradient-to-r from-champagne-50 to-champagne-100/50">
                <div className="flex items-center space-x-3">
                  <div className="bg-gradient-to-br from-champagne-400 to-champagne-600 p-2 rounded-xl">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-tech-text">{t.exchangeRate || '实时汇率'}</h2>
                    <p className="text-xs text-tech-sub">Binance P2P 商家数据</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleRefresh}
                    disabled={refreshing || loading}
                    className="p-2 hover:bg-white/60 rounded-full transition-colors disabled:opacity-50"
                    aria-label="Refresh"
                  >
                    <RefreshCw className={`w-5 h-5 text-champagne-600 ${refreshing ? 'animate-spin' : ''}`} />
                  </button>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-white/60 rounded-full transition-colors"
                    aria-label="Close"
                  >
                    <X className="w-5 h-5 text-tech-sub" />
                  </button>
                </div>
              </div>

              {/* Payment Method Tabs */}
              <div className="flex border-b border-gray-200 bg-gray-50/50">
                <button
                  onClick={() => handlePaymentMethodChange('alipay')}
                  className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                    paymentMethod === 'alipay'
                      ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  🔵 支付宝
                </button>
                <button
                  onClick={() => handlePaymentMethodChange('wechat')}
                  className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                    paymentMethod === 'wechat'
                      ? 'text-green-600 border-b-2 border-green-600 bg-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  🟢 微信
                </button>
                <button
                  onClick={() => handlePaymentMethodChange('bank')}
                  className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                    paymentMethod === 'bank'
                      ? 'text-purple-600 border-b-2 border-purple-600 bg-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  💳 银行卡
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-4">
                {loading && !data ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <RefreshCw className="w-8 h-8 text-champagne-600 animate-spin mb-4" />
                    <p className="text-tech-sub">加载中...</p>
                  </div>
                ) : error ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <p className="text-red-600 mb-4">{error}</p>
                    <button
                      onClick={handleRefresh}
                      className="px-4 py-2 bg-champagne-500 text-white rounded-xl hover:bg-champagne-600 transition-colors"
                    >
                      重试
                    </button>
                  </div>
                ) : data && data.merchants.length > 0 ? (
                  <>
                    {/* Market Stats */}
                    <div className="mb-4 p-4 bg-gradient-to-r from-champagne-50 to-blue-50 rounded-2xl border border-champagne-200/50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-tech-sub">市场概况</span>
                        <div className="flex items-center space-x-1 text-champagne-600">
                          <Zap className="w-3 h-3" />
                          <span className="text-xs font-medium">实时更新</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div>
                          <p className="text-xs text-tech-sub">最低</p>
                          <p className="text-sm font-bold text-tech-text">¥{data.market_stats.min_price.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-tech-sub">最高</p>
                          <p className="text-sm font-bold text-tech-text">¥{data.market_stats.max_price.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-tech-sub">均价</p>
                          <p className="text-sm font-bold text-champagne-600">¥{data.market_stats.avg_price.toFixed(2)}</p>
                        </div>
                      </div>
                    </div>

                    {/* Merchant List */}
                    <div className="space-y-3">
                      {data.merchants.map((merchant, idx) => (
                        <motion.div
                          key={merchant.rank}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.05 }}
                          className="p-4 bg-white border border-gray-200 rounded-2xl hover:shadow-md transition-all"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-2 flex-1">
                              <span className="text-lg">{getRankEmoji(merchant.rank)}</span>
                              <div className="flex-1 min-w-0">
                                <p className="font-bold text-tech-text truncate">{merchant.merchant_name}</p>
                                <p className="text-xs text-tech-sub">
                                  {merchant.finish_rate > 0 
                                    ? `完成率: ${(merchant.finish_rate * 100).toFixed(0)}% • `
                                    : ''
                                  }
                                  成单: {merchant.trade_count.toLocaleString()} 笔
                                </p>
                              </div>
                            </div>
                            <div className="text-right ml-3">
                              <p className="text-xl font-bold text-transparent bg-clip-text bg-gradient-gold">
                                ¥{merchant.price.toFixed(2)}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                            <p className="text-xs text-tech-sub">
                              限额: ¥{formatAmount(merchant.min_amount)} - ¥{formatAmount(merchant.max_amount)}
                            </p>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12">
                    <p className="text-tech-sub">暂无数据</p>
                  </div>
                )}
              </div>

              {/* Pagination Footer */}
              {data && totalPages > 1 && (
                <div className="flex items-center justify-between p-4 border-t border-gray-200 bg-gray-50/50">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1 || loading}
                    className="flex items-center space-x-1 px-4 py-2 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span className="text-sm font-medium">上一页</span>
                  </button>
                  <span className="text-sm text-tech-sub">
                    第 {page} / {totalPages} 页
                  </span>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages || loading}
                    className="flex items-center space-x-1 px-4 py-2 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <span className="text-sm font-medium">下一页</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
