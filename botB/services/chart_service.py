"""
Chart generation service for Bot B
Generates various charts for data visualization
"""
import logging
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import numpy as np
from database import db

logger = logging.getLogger(__name__)

# Configure matplotlib to support Chinese
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Chart style configuration
CHART_STYLE = {
    'figure_size': (10, 6),
    'dpi': 100,
    'facecolor': 'white',
    'edgecolor': 'none',
    'line_width': 2,
    'grid_alpha': 0.3,
    'title_fontsize': 14,
    'label_fontsize': 10,
    'legend_fontsize': 9
}


def generate_transaction_trend_chart(
    group_id: Optional[int] = None,
    days: int = 7
) -> Optional[bytes]:
    """
    Generate transaction trend chart (line chart) for the last N days.
    
    Args:
        group_id: Optional Telegram group ID. If None, shows global stats.
        days: Number of days to show (7 or 30)
        
    Returns:
        PNG image bytes or None if error
    """
    try:
        # Get transaction data for the last N days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query transactions from database
        if group_id:
            transactions = db.get_transactions_by_group(group_id)
        else:
            # Get all transactions (need a new method)
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, cny_amount, usdt_amount
                FROM transactions
                WHERE created_at >= ? AND created_at <= ?
                ORDER BY created_at
            """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            transactions = [{'created_at': row[0], 'cny_amount': row[1], 'usdt_amount': row[2]} 
                          for row in cursor.fetchall()]
        
        if not transactions:
            logger.warning(f"No transactions found for the last {days} days")
            return None
        
        # Filter transactions by date range
        filtered_transactions = []
        for tx in transactions:
            try:
                tx_date = datetime.strptime(tx['created_at'][:10], '%Y-%m-%d')
                if start_date.date() <= tx_date.date() <= end_date.date():
                    filtered_transactions.append(tx)
            except (ValueError, TypeError):
                continue
        
        if not filtered_transactions:
            return None
        
        # Group by date
        daily_data = {}
        for tx in filtered_transactions:
            date_str = tx['created_at'][:10]
            if date_str not in daily_data:
                daily_data[date_str] = {'count': 0, 'total_cny': 0.0, 'total_usdt': 0.0}
            daily_data[date_str]['count'] += 1
            daily_data[date_str]['total_cny'] += float(tx['cny_amount'] or 0)
            daily_data[date_str]['total_usdt'] += float(tx['usdt_amount'] or 0)
        
        # Sort by date
        sorted_dates = sorted(daily_data.keys())
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in sorted_dates]
        counts = [daily_data[d]['count'] for d in sorted_dates]
        cny_amounts = [daily_data[d]['total_cny'] for d in sorted_dates]
        usdt_amounts = [daily_data[d]['total_usdt'] for d in sorted_dates]
        
        # Create figure with two y-axes
        fig, ax1 = plt.subplots(figsize=CHART_STYLE['figure_size'], dpi=CHART_STYLE['dpi'])
        ax1.set_facecolor(CHART_STYLE['facecolor'])
        
        # Plot transaction count
        ax1.plot(dates, counts, 'o-', color='#2E86AB', linewidth=CHART_STYLE['line_width'],
                label='Transaction Count', marker='o', markersize=6)
        ax1.set_xlabel('Date', fontsize=CHART_STYLE['label_fontsize'])
        ax1.set_ylabel('Transaction Count', fontsize=CHART_STYLE['label_fontsize'], color='#2E86AB')
        ax1.tick_params(axis='y', labelcolor='#2E86AB')
        ax1.grid(True, alpha=CHART_STYLE['grid_alpha'])
        
        # Format x-axis dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 7)))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Create second y-axis for amounts
        ax2 = ax1.twinx()
        ax2.plot(dates, cny_amounts, 's-', color='#A23B72', linewidth=CHART_STYLE['line_width'],
                label='Total CNY', marker='s', markersize=6, alpha=0.7)
        ax2.set_ylabel('Total Amount (CNY)', fontsize=CHART_STYLE['label_fontsize'], color='#A23B72')
        ax2.tick_params(axis='y', labelcolor='#A23B72')
        
        # Title
        scope = f"Group {group_id}" if group_id else "Global"
        title = f"Transaction Trend - Last {days} Days ({scope})"
        ax1.set_title(title, fontsize=CHART_STYLE['title_fontsize'], fontweight='bold', pad=20)
        
        # Legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=CHART_STYLE['legend_fontsize'])
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'], bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        buf.close()
        plt.close(fig)
        
        logger.info(f"Generated transaction trend chart for {days} days")
        return image_bytes
        
    except Exception as e:
        logger.error(f"Error generating transaction trend chart: {e}", exc_info=True)
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_transaction_volume_chart(
    group_id: Optional[int] = None,
    days: int = 7
) -> Optional[bytes]:
    """
    Generate transaction volume bar chart for the last N days.
    
    Args:
        group_id: Optional Telegram group ID. If None, shows global stats.
        days: Number of days to show
        
    Returns:
        PNG image bytes or None if error
    """
    try:
        # Get transaction data (similar to trend chart)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        if group_id:
            transactions = db.get_transactions_by_group(group_id)
        else:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, cny_amount, usdt_amount
                FROM transactions
                WHERE created_at >= ? AND created_at <= ?
                ORDER BY created_at
            """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            transactions = [{'created_at': row[0], 'cny_amount': row[1], 'usdt_amount': row[2]} 
                          for row in cursor.fetchall()]
        
        if not transactions:
            return None
        
        # Filter and group by date
        daily_data = {}
        for tx in transactions:
            try:
                date_str = tx['created_at'][:10]
                tx_date = datetime.strptime(date_str, '%Y-%m-%d')
                if start_date.date() <= tx_date.date() <= end_date.date():
                    if date_str not in daily_data:
                        daily_data[date_str] = {'total_cny': 0.0, 'total_usdt': 0.0}
                    daily_data[date_str]['total_cny'] += float(tx['cny_amount'] or 0)
                    daily_data[date_str]['total_usdt'] += float(tx['usdt_amount'] or 0)
            except (ValueError, TypeError):
                continue
        
        if not daily_data:
            return None
        
        # Sort by date
        sorted_dates = sorted(daily_data.keys())
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in sorted_dates]
        cny_amounts = [daily_data[d]['total_cny'] for d in sorted_dates]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=CHART_STYLE['figure_size'], dpi=CHART_STYLE['dpi'])
        ax.set_facecolor(CHART_STYLE['facecolor'])
        
        # Create bars
        bars = ax.bar(dates, cny_amounts, color='#06A77D', alpha=0.8, width=0.8)
        
        # Format values on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=8)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 7)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Labels and title
        ax.set_xlabel('Date', fontsize=CHART_STYLE['label_fontsize'])
        ax.set_ylabel('Total CNY Amount', fontsize=CHART_STYLE['label_fontsize'])
        scope = f"Group {group_id}" if group_id else "Global"
        title = f"Transaction Volume - Last {days} Days ({scope})"
        ax.set_title(title, fontsize=CHART_STYLE['title_fontsize'], fontweight='bold', pad=20)
        ax.grid(True, alpha=CHART_STYLE['grid_alpha'], axis='y')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'], bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        buf.close()
        plt.close(fig)
        
        logger.info(f"Generated transaction volume chart for {days} days")
        return image_bytes
        
    except Exception as e:
        logger.error(f"Error generating transaction volume chart: {e}", exc_info=True)
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_user_distribution_chart(
    group_id: Optional[int] = None,
    top_n: int = 10
) -> Optional[bytes]:
    """
    Generate user distribution pie chart (top N users by transaction count).
    
    Args:
        group_id: Optional Telegram group ID. If None, shows global stats.
        top_n: Number of top users to show
        
    Returns:
        PNG image bytes or None if error
    """
    try:
        # Get user transaction counts
        conn = db.connect()
        cursor = conn.cursor()
        
        if group_id:
            cursor.execute("""
                SELECT user_id, first_name, username, COUNT(*) as count
                FROM transactions
                WHERE group_id = ?
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT ?
            """, (group_id, top_n))
        else:
            cursor.execute("""
                SELECT user_id, first_name, username, COUNT(*) as count
                FROM transactions
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT ?
            """, (top_n,))
        
        rows = cursor.fetchall()
        if not rows:
            return None
        
        # Prepare data for pie chart
        labels = []
        sizes = []
        
        for row in rows:
            user_id = row[0]
            first_name = row[1]
            username = row[2]
            count = row[3]
            
            name = first_name or username or f"User {user_id}"
            if len(name) > 10:
                name = name[:10] + '...'
            labels.append(name)
            sizes.append(count)
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=CHART_STYLE['figure_size'], dpi=CHART_STYLE['dpi'])
        ax.set_facecolor(CHART_STYLE['facecolor'])
        
        # Color palette
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 9})
        
        # Title
        scope = f"Group {group_id}" if group_id else "Global"
        title = f"Top {top_n} Users by Transaction Count ({scope})"
        ax.set_title(title, fontsize=CHART_STYLE['title_fontsize'], fontweight='bold', pad=20)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'], bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        buf.close()
        plt.close(fig)
        
        logger.info(f"Generated user distribution chart (top {top_n} users)")
        return image_bytes
        
    except Exception as e:
        logger.error(f"Error generating user distribution chart: {e}", exc_info=True)
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_price_trend_chart(
    days: int = 7
) -> Optional[bytes]:
    """
    Generate price trend chart for the last N days.
    
    Args:
        days: Number of days to show
        
    Returns:
        PNG image bytes or None if error
    """
    try:
        # Get price history directly from database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT base_price, final_price, created_at
            FROM price_history
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at
        """, (start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')))
        rows = cursor.fetchall()
        
        if not rows:
            return None
        
        price_history = [{'final_price': float(row['final_price']), 'created_at': row['created_at']} 
                        for row in rows]
        
        if not price_history:
            return None
        
        # Prepare data
        timestamps = []
        prices = []
        
        for record in price_history:
            try:
                ts = datetime.strptime(record['created_at'][:19], '%Y-%m-%d %H:%M:%S')
                if start_date <= ts <= end_date:
                    timestamps.append(ts)
                    prices.append(float(record['final_price']))
            except (ValueError, TypeError):
                continue
        
        if not timestamps:
            return None
        
        # Create line chart
        fig, ax = plt.subplots(figsize=CHART_STYLE['figure_size'], dpi=CHART_STYLE['dpi'])
        ax.set_facecolor(CHART_STYLE['facecolor'])
        
        # Plot price line
        ax.plot(timestamps, prices, 'o-', color='#F18F01', linewidth=CHART_STYLE['line_width'],
               marker='o', markersize=4, label='USDT/CNY Price')
        
        # Add min/max/avg lines
        if len(prices) > 0:
            min_price = min(prices)
            max_price = max(prices)
            avg_price = np.mean(prices)
            
            ax.axhline(y=min_price, color='green', linestyle='--', alpha=0.5, label=f'Min: {min_price:.4f}')
            ax.axhline(y=max_price, color='red', linestyle='--', alpha=0.5, label=f'Max: {max_price:.4f}')
            ax.axhline(y=avg_price, color='blue', linestyle='--', alpha=0.5, label=f'Avg: {avg_price:.4f}')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12 if days <= 1 else 24))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Labels and title
        ax.set_xlabel('Time', fontsize=CHART_STYLE['label_fontsize'])
        ax.set_ylabel('Price (CNY)', fontsize=CHART_STYLE['label_fontsize'])
        title = f"USDT/CNY Price Trend - Last {days} Days"
        ax.set_title(title, fontsize=CHART_STYLE['title_fontsize'], fontweight='bold', pad=20)
        ax.grid(True, alpha=CHART_STYLE['grid_alpha'])
        ax.legend(loc='best', fontsize=CHART_STYLE['legend_fontsize'])
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'], bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        buf.close()
        plt.close(fig)
        
        logger.info(f"Generated price trend chart for {days} days")
        return image_bytes
        
    except Exception as e:
        logger.error(f"Error generating price trend chart: {e}", exc_info=True)
        if 'fig' in locals():
            plt.close(fig)
        return None

