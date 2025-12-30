"""
Configuration loader for OTC Group Management Bot (Bot B)
Loads environment variables from .env file in root directory
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env file in root directory (parent of botB/)
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
    """Configuration class for Bot B settings"""
    
    # Bot Token from BOT_TOKEN_B environment variable (Bot B)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN_B", "")
    
    # Initial admin user IDs (can be extended later)
    # Can be set via ADMIN_IDS environment variable (comma-separated)
    # Format: ADMIN_IDS=123456789,987654321
    # This will be the same as Bot A if both use the same .env file
    INITIAL_ADMINS: list[int] = _parse_admin_ids()
    
    # CoinGecko API endpoint for USDT/CNY
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    
    # Default fallback price (USDT/CNY) if CoinGecko API fails
    DEFAULT_FALLBACK_PRICE: float = 7.20
    
    # MiniApp URL
    MINIAPP_URL: str = os.getenv("MINIAPP_URL", "https://50zf.usdt2026.cc")
    
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
            raise ValueError(
                "BOT_TOKEN_B is not set. Please ensure the second line of .env "
                "contains the Bot B token, or set BOT_TOKEN_B environment variable."
            )
        return True

