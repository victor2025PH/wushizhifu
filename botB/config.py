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


class Config:
    """Configuration class for Bot B settings"""
    
    # Bot Token from BOT_TOKEN_B environment variable (Bot B)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN_B", "")
    
    # Initial admin user IDs (can be extended later)
    # Can be set via ADMIN_IDS environment variable (comma-separated)
    # Format: ADMIN_IDS=123456789,987654321
    # This will be the same as Bot A if both use the same .env file
    _admin_ids_str: str = os.getenv("ADMIN_IDS", "")
    if _admin_ids_str:
        # Parse from environment variable
        INITIAL_ADMINS: list[int] = [
            int(uid.strip()) for uid in _admin_ids_str.split(",") if uid.strip().isdigit()
        ]
    else:
        # Fallback to default admins
        INITIAL_ADMINS: list[int] = [
            7974525763,
            5433982810
        ]
    
    # Database file path
    DB_PATH: str = "otc_bot.db"
    
    # CoinGecko API endpoint for USDT/CNY
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    
    # Default fallback price (USDT/CNY) if CoinGecko API fails
    DEFAULT_FALLBACK_PRICE: float = 7.20
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN_B is not set. Please ensure the second line of .env "
                "contains the Bot B token, or set BOT_TOKEN_B environment variable."
            )
        return True

