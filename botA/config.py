"""
Configuration loader for WuShiPay Telegram Bot (Bot A)
Loads environment variables from .env file in root directory
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env file in root directory (parent of botA/)
root_dir = Path(__file__).parent.parent
env_path = root_dir / '.env'

# Load environment variables from .env file
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to current directory or environment variables
    load_dotenv()


def _parse_admin_ids() -> list[int]:
    """Parse admin IDs from environment variable or return defaults"""
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        # Parse from environment variable (comma-separated)
        return [
            int(uid.strip()) for uid in admin_ids_str.split(",") if uid.strip().isdigit()
        ]
    else:
        # Fallback to default admins
        return [
            7974525763,
            5433982810
        ]


class Config:
    """Configuration class for bot settings"""
    
    # Bot Token from environment variable (Bot A uses BOT_TOKEN)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Initial admin user IDs (will be created on database initialization)
    # Can be set via ADMIN_IDS environment variable (comma-separated)
    # Format: ADMIN_IDS=123456789,987654321
    INITIAL_ADMINS: list[int] = _parse_admin_ids()
    
    # MiniApp URL
    MINIAPP_URL: str = "https://50zf.usdt2026.cc"
    
    # Support Telegram username
    SUPPORT_USERNAME: str = "wushizhifu_jianglai"
    SUPPORT_URL: str = f"https://t.me/{SUPPORT_USERNAME}"
    
    @classmethod
    def get_miniapp_url(cls, view: str = "dashboard", provider: str = None) -> str:
        """Generate MiniApp URL with parameters"""
        url = f"{cls.MINIAPP_URL}?view={view}"
        if provider:
            url += f"&provider={provider}"
        return url
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set in environment variables or .env file")
        return True

