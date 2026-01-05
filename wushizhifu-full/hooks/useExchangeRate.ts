import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { apiClient } from '../api';
import { EXCHANGE_RATE_CNY_USDT } from '../types';

interface ExchangeRateContextType {
  rate: number;
  loading: boolean;
  refresh: () => void;
}

const ExchangeRateContext = createContext<ExchangeRateContextType>({
  rate: EXCHANGE_RATE_CNY_USDT,
  loading: false,
  refresh: () => {}
});

export const ExchangeRateProvider = ({ children }: { children: ReactNode }) => {
  const [rate, setRate] = useState<number>(EXCHANGE_RATE_CNY_USDT);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchRate = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getBinanceP2P({
        payment_method: 'alipay',
        rows: 10,
        page: 1
      });
      if (data && data.market_stats && data.market_stats.avg_price > 0) {
        setRate(data.market_stats.avg_price);
      }
    } catch (error) {
      console.error('Failed to fetch exchange rate:', error);
      // Keep using default rate on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchRate();

    // Refresh every 60 seconds
    const intervalId = setInterval(fetchRate, 60000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <ExchangeRateContext.Provider value={{ rate, loading, refresh: fetchRate }}>
      {children}
    </ExchangeRateContext.Provider>
  );
};

export const useExchangeRate = () => {
  const context = useContext(ExchangeRateContext);
  if (!context) {
    // Fallback if context is not available
    return {
      rate: EXCHANGE_RATE_CNY_USDT,
      loading: false,
      refresh: () => {}
    };
  }
  return context;
};
