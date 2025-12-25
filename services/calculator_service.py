"""
Calculator service for fee and exchange rate calculations
"""
from typing import Tuple
from database.rate_repository import RateRepository
import logging

logger = logging.getLogger(__name__)


class CalculatorService:
    """Service for calculator operations"""
    
    @staticmethod
    def calculate_fee(amount: float, channel: str = "alipay", vip_level: int = 0) -> dict:
        """
        Calculate transaction fee and actual amount.
        
        Args:
            amount: Transaction amount
            channel: Payment channel (alipay, wechat)
            vip_level: VIP level (0-3)
            
        Returns:
            Dictionary with fee calculation results
        """
        try:
            fee, actual_amount = RateRepository.calculate_fee(amount, channel, vip_level)
            
            rate_config = RateRepository.get_rate(channel, vip_level)
            rate_percentage = float(rate_config['rate_percentage']) * 100 if rate_config else 0.6
            
            return {
                "amount": amount,
                "channel": channel,
                "vip_level": vip_level,
                "rate_percentage": rate_percentage,
                "fee": fee,
                "actual_amount": actual_amount
            }
        except Exception as e:
            logger.error(f"Error calculating fee: {e}")
            raise
    
    @staticmethod
    def convert_currency(amount: float, from_currency: str = "USDT", 
                        to_currency: str = "CNY", exchange_rate: float = 7.42) -> dict:
        """
        Convert currency.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            exchange_rate: Exchange rate
            
        Returns:
            Dictionary with conversion results
        """
        try:
            converted_amount = round(amount * exchange_rate, 2)
            
            return {
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": exchange_rate,
                "converted_amount": converted_amount
            }
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            raise
    
    @staticmethod
    def format_amount(amount: float) -> str:
        """Format amount with currency symbol"""
        return f"¥{amount:,.2f}"

