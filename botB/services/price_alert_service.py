"""
Price alert service for Bot B
Handles price monitoring and alert notifications
"""
import logging
from typing import Optional, List, Dict
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from services.price_service import get_price_with_markup

logger = logging.getLogger(__name__)


async def check_price_alerts(group_id: Optional[int] = None) -> List[Dict]:
    """
    Check all active price alerts and return alerts that should be triggered.
    
    Args:
        group_id: Optional group ID for group-specific price check
        
    Returns:
        List of alerts that should be triggered
    """
    try:
        # Get current price
        final_price, error_msg, base_price, markup = get_price_with_markup(group_id)
        
        if final_price is None:
            logger.warning(f"Failed to get price for alert checking: {error_msg}")
            return []
        
        # Save price history
        db.save_price_history(base_price, final_price, markup, 'binance_p2p')
        
        # Get all active alerts
        active_alerts = db.get_active_alerts()
        
        triggered_alerts = []
        
        for alert in active_alerts:
            should_trigger = False
            
            # Check alert condition based on operator
            operator = alert['comparison_operator']
            threshold = alert['threshold_value']
            
            if operator == '>':
                should_trigger = final_price > threshold
            elif operator == '>=':
                should_trigger = final_price >= threshold
            elif operator == '<':
                should_trigger = final_price < threshold
            elif operator == '<=':
                should_trigger = final_price <= threshold
            
            if should_trigger:
                # Rate limiting: Don't notify too frequently (at least 5 minutes between notifications)
                import datetime
                last_notified = alert.get('last_notified_at')
                if last_notified:
                    try:
                        last_time = datetime.datetime.fromisoformat(last_notified.replace('Z', '+00:00'))
                        if isinstance(last_time, str):
                            # Handle SQLite timestamp format
                            from dateutil import parser
                            last_time = parser.parse(last_notified)
                        time_diff = datetime.datetime.now() - last_time.replace(tzinfo=None)
                        if time_diff.total_seconds() < 300:  # 5 minutes
                            continue  # Skip if notified recently
                    except:
                        pass  # If parsing fails, allow notification
                
                triggered_alerts.append(alert)
        
        return triggered_alerts
        
    except Exception as e:
        logger.error(f"Error checking price alerts: {e}", exc_info=True)
        return []


async def send_alert_notification(context: ContextTypes.DEFAULT_TYPE, alert: Dict, current_price: float):
    """
    Send price alert notification to user.
    
    Args:
        context: Bot context
        alert: Alert dictionary
        current_price: Current price that triggered the alert
    """
    try:
        user_id = alert['user_id']
        alert_type = alert['alert_type']
        threshold = alert['threshold_value']
        operator = alert['comparison_operator']
        
        # Format operator display
        operator_display = {
            '>': '高于',
            '>=': '高于或等于',
            '<': '低于',
            '<=': '低于或等于'
        }.get(operator, operator)
        
        message = (
            f"🔔 <b>价格预警通知</b>\n\n"
            f"当前价格已{operator_display}您设置的阈值！\n\n"
            f"📊 当前价格: <b>{current_price:.4f} CNY</b>\n"
            f"📈 预警阈值: {operator} {threshold:.4f} CNY\n\n"
            f"💡 提示：您可以发送 /alerts 查看和管理所有预警设置"
        )
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML"
        )
        
        # Update alert notification
        db.update_alert_notification(alert['id'])
        
        logger.info(f"Price alert notification sent to user {user_id}: price {current_price} {operator} {threshold}")
        
    except Exception as e:
        logger.error(f"Error sending alert notification: {e}", exc_info=True)


async def monitor_price_alerts(context: ContextTypes.DEFAULT_TYPE):
    """
    Background task to monitor price alerts.
    Should be called periodically (e.g., every 5 minutes).
    
    Args:
        context: Bot context
    """
    try:
        # Check alerts (for global price, group_id=None)
        triggered = await check_price_alerts(group_id=None)
        
        if not triggered:
            return
        
        # Get current price for notifications
        final_price, _, _, _ = get_price_with_markup(group_id=None)
        
        if final_price is None:
            return
        
        # Send notifications
        for alert in triggered:
            await send_alert_notification(context, alert, final_price)
        
        logger.info(f"Processed {len(triggered)} price alerts")
        
    except Exception as e:
        logger.error(f"Error in price alert monitoring: {e}", exc_info=True)

