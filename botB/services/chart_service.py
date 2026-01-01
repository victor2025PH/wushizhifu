"""
Chart service for generating text-based charts and visualizations
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ChartService:
    """Service for generating text charts"""
    
    # Block characters for charts (Unicode)
    BLOCKS = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    @staticmethod
    def generate_bar_chart(data: List[Dict], value_key: str, label_key: str, 
                          max_width: int = 30, height: int = 8) -> str:
        """
        Generate a text-based bar chart.
        
        Args:
            data: List of dictionaries with data points
            value_key: Key in dict for numeric value
            label_key: Key in dict for label text
            max_width: Maximum width of chart in characters
            height: Height of chart in lines
            
        Returns:
            String representation of the chart
        """
        if not data:
            return "暂无数据"
        
        # Extract values and labels
        values = [float(item.get(value_key, 0) or 0) for item in data]
        labels = [str(item.get(label_key, ''))[:15] for item in data]  # Limit label length
        
        if not values or max(values) == 0:
            return "数据全部为0"
        
        # Normalize values to 0-1 range
        max_value = max(values)
        normalized = [v / max_value if max_value > 0 else 0 for v in values]
        
        # Generate chart lines
        chart_lines = []
        
        # Add header
        chart_lines.append("┌" + "─" * (max_width + 2) + "┐")
        
        # Generate bars
        for i in range(len(data)):
            bar_width = int(normalized[i] * max_width)
            bar = "█" * bar_width
            if bar_width < max_width:
                bar += "░" * (max_width - bar_width)
            
            # Format label and value
            label = labels[i]
            value = values[i]
            value_str = f"{value:,.0f}" if value >= 1 else f"{value:.2f}"
            
            # Truncate label if too long
            label_display = label[:12] if len(label) > 12 else label
            label_display = label_display.ljust(12)
            
            chart_lines.append(f"│ {label_display} {bar} {value_str:>8} │")
        
        # Add footer
        chart_lines.append("└" + "─" * (max_width + 2) + "┘")
        
        return "\n".join(chart_lines)
    
    @staticmethod
    def generate_line_chart(data: List[Dict], value_key: str, label_key: str,
                           width: int = 50, height: int = 10) -> str:
        """
        Generate a text-based line chart.
        
        Args:
            data: List of dictionaries with data points (ordered by time)
            value_key: Key in dict for numeric value
            label_key: Key in dict for label text
            width: Width of chart in characters
            height: Height of chart in lines
            
        Returns:
            String representation of the chart
        """
        if not data or len(data) < 2:
            return "需要至少2个数据点"
        
        values = [float(item.get(value_key, 0) or 0) for item in data]
        labels = [str(item.get(label_key, ''))[:10] for item in data]
        
        if max(values) == 0:
            return "数据全部为0"
        
        # Normalize values
        max_value = max(values)
        min_value = min(values)
        value_range = max_value - min_value if max_value != min_value else 1
        
        # Create grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw axes
        for i in range(height):
            grid[i][0] = '│'
        for j in range(width):
            grid[height - 1][j] = '─'
        
        grid[height - 1][0] = '└'
        
        # Plot points
        points = []
        for i, value in enumerate(values):
            x = int((i / (len(values) - 1)) * (width - 2)) + 1 if len(values) > 1 else 1
            y = height - 2 - int(((value - min_value) / value_range) * (height - 2))
            y = max(0, min(height - 2, y))
            points.append((x, y))
        
        # Draw line
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # Simple line drawing (Bresenham-like)
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            
            x, y = x1, y1
            while True:
                if 0 <= y < height - 1 and 1 <= x < width:
                    grid[y][x] = '●'
                
                if x == x2 and y == y2:
                    break
                
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x += sx
                if e2 < dx:
                    err += dx
                    y += sy
        
        # Convert grid to string
        lines = []
        for row in grid:
            lines.append(''.join(row))
        
        # Add labels at bottom (every few points to avoid crowding)
        label_line = ' ' * (width + 1)
        step = max(1, len(labels) // 5)
        for i in range(0, len(labels), step):
            label = labels[i][:5]
            x = int((i / (len(values) - 1)) * (width - 2)) + 1 if len(values) > 1 else 1
            if x + len(label) < width:
                label_line = label_line[:x] + label + label_line[x + len(label):]
        
        lines.append(label_line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_simple_bar(data: List[Dict], value_key: str, label_key: str,
                           max_bars: int = 10) -> str:
        """
        Generate a simple text bar chart (compact version).
        
        Args:
            data: List of dictionaries with data points
            value_key: Key in dict for numeric value
            label_key: Key in dict for label text
            max_bars: Maximum number of bars to show
            
        Returns:
            String representation of the chart
        """
        if not data:
            return "暂无数据"
        
        # Take top N items
        sorted_data = sorted(data, key=lambda x: float(x.get(value_key, 0) or 0), reverse=True)
        top_data = sorted_data[:max_bars]
        
        values = [float(item.get(value_key, 0) or 0) for item in top_data]
        labels = [str(item.get(label_key, ''))[:20] for item in top_data]
        
        if max(values) == 0:
            return "数据全部为0"
        
        # Normalize
        max_value = max(values)
        max_bar_length = 30
        
        lines = []
        for i, (label, value) in enumerate(zip(labels, values), 1):
            bar_length = int((value / max_value) * max_bar_length) if max_value > 0 else 0
            bar = "█" * bar_length
            
            value_str = f"{value:,.0f}" if value >= 1 else f"{value:.2f}"
            label_display = label.ljust(20)
            
            lines.append(f"{i:2}. {label_display} {bar} {value_str:>10}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_trend_indicator(current: float, previous: float) -> str:
        """
        Generate a trend indicator (↑ ↓ →).
        
        Args:
            current: Current value
            previous: Previous value
            
        Returns:
            Trend indicator string
        """
        if previous == 0:
            if current > 0:
                return "📈 新增"
            else:
                return "➡️ 无变化"
        
        change = current - previous
        change_percent = (change / previous) * 100
        
        if change_percent > 5:
            return f"📈 ↑ {change_percent:+.1f}%"
        elif change_percent < -5:
            return f"📉 ↓ {change_percent:+.1f}%"
        else:
            return f"➡️ → {change_percent:+.1f}%"
