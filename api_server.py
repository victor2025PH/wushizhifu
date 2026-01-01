"""
FastAPI server for MiniApp backend API
Provides endpoints for user authentication, data synchronization, and transaction management
"""
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import hmac
import hashlib
import os
import logging
from urllib.parse import parse_qs, unquote
from datetime import datetime

from config import Config
from database.user_repository import UserRepository
from database.transaction_repository import TransactionRepository
from database.rate_repository import RateRepository
from database.video_repository import VideoRepository
import httpx
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WuShiPay API", version="1.0.0")

# CORS middleware for MiniApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    language_code: Optional[str] = None


class AuthRequest(BaseModel):
    init_data: str
    user: Optional[TelegramUser] = None


class UserResponse(BaseModel):
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: Optional[str]
    is_premium: bool
    vip_level: int
    total_transactions: int
    total_amount: float
    created_at: str
    last_active_at: str


class TransactionResponse(BaseModel):
    transaction_id: int
    order_id: str
    transaction_type: str
    payment_channel: str
    amount: float
    fee: float
    actual_amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: str
    paid_at: Optional[str]
    expired_at: Optional[str]


class StatisticsResponse(BaseModel):
    total_transactions: int
    total_receive: int
    total_pay: int
    total_amount: float
    vip_level: int


def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Verify Telegram WebApp initData signature.
    
    According to Telegram Bot API documentation:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    
    Args:
        init_data: Telegram WebApp initData string
        bot_token: Bot token for verification
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Parse init_data
        parsed = parse_qs(init_data)
        
        # Get hash from init_data
        received_hash = parsed.get('hash', [None])[0]
        if not received_hash:
            logger.warning("No hash in init_data")
            return False
        
        # Remove hash from data and sort
        data_check = []
        for key, value in parsed.items():
            if key != 'hash':
                data_check.append(f"{key}={value[0]}")
        
        # Sort and join with newline
        data_check_string = '\n'.join(sorted(data_check))
        
        # Create secret key: HMAC-SHA256("WebAppData", bot_token)
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Calculate hash: HMAC-SHA256(secret_key, data_check_string)
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        is_valid = calculated_hash == received_hash
        if not is_valid:
            logger.warning(f"Hash mismatch: calculated={calculated_hash[:8]}..., received={received_hash[:8]}...")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying init_data: {e}", exc_info=True)
        return False


def parse_init_data(init_data: str) -> dict:
    """Parse Telegram initData and extract user information"""
    try:
        parsed = parse_qs(init_data)
        user_str = parsed.get('user', [None])[0]
        if user_str:
            import json
            user_data = json.loads(unquote(user_str))
            return user_data
        return {}
    except Exception as e:
        logger.error(f"Error parsing init_data: {e}")
        return {}


async def verify_auth(x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")) -> dict:
    """
    Dependency to verify Telegram authentication.
    
    Args:
        x_telegram_init_data: Telegram WebApp initData from header (X-Telegram-Init-Data)
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException if authentication fails
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-Init-Data header")
    
    # Verify signature
    if not verify_telegram_init_data(x_telegram_init_data, Config.BOT_TOKEN):
        logger.warning("Invalid init_data signature")
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    # Parse user data
    user_data = parse_init_data(x_telegram_init_data)
    if not user_data:
        raise HTTPException(status_code=401, detail="No user data in init_data")
    
    return user_data


@app.get("/")
async def root():
    """API health check"""
    return {"status": "ok", "service": "WuShiPay API", "version": "1.0.0"}


@app.post("/api/auth/sync", response_model=UserResponse)
async def sync_user(auth_request: AuthRequest):
    """
    Sync user information from MiniApp to database.
    
    This endpoint receives Telegram user info from MiniApp and
    synchronizes it with the Bot's database.
    """
    try:
        # Verify init_data if provided
        if auth_request.init_data:
            if not verify_telegram_init_data(auth_request.init_data, Config.BOT_TOKEN):
                raise HTTPException(status_code=401, detail="Invalid init_data")
            
            # Parse user from init_data if not provided
            if not auth_request.user:
                user_data = parse_init_data(auth_request.init_data)
                if user_data:
                    auth_request.user = TelegramUser(**user_data)
        
        if not auth_request.user:
            raise HTTPException(status_code=400, detail="No user data provided")
        
        # Sync user to database
        user_dict = UserRepository.create_or_update_user(
            user_id=auth_request.user.id,
            username=auth_request.user.username,
            first_name=auth_request.user.first_name,
            last_name=auth_request.user.last_name,
            language_code=auth_request.user.language_code,
            is_premium=False  # Can be enhanced later
        )
        
        # Format response
        return UserResponse(
            user_id=user_dict['user_id'],
            username=user_dict.get('username'),
            first_name=user_dict.get('first_name'),
            last_name=user_dict.get('last_name'),
            language_code=user_dict.get('language_code'),
            is_premium=bool(user_dict.get('is_premium', 0)),
            vip_level=user_dict.get('vip_level', 0),
            total_transactions=user_dict.get('total_transactions', 0),
            total_amount=float(user_dict.get('total_amount', 0)),
            created_at=user_dict.get('created_at', ''),
            last_active_at=user_dict.get('last_active_at', '')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user(user_data: dict = Depends(verify_auth)):
    """
    Get current user information from database.
    """
    try:
        user_id = user_data.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user data")
        
        user_dict = UserRepository.get_user(user_id)
        if not user_dict:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=user_dict['user_id'],
            username=user_dict.get('username'),
            first_name=user_dict.get('first_name'),
            last_name=user_dict.get('last_name'),
            language_code=user_dict.get('language_code'),
            is_premium=bool(user_dict.get('is_premium', 0)),
            vip_level=user_dict.get('vip_level', 0),
            total_transactions=user_dict.get('total_transactions', 0),
            total_amount=float(user_dict.get('total_amount', 0)),
            created_at=user_dict.get('created_at', ''),
            last_active_at=user_dict.get('last_active_at', '')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/user/statistics", response_model=StatisticsResponse)
async def get_user_statistics(user_data: dict = Depends(verify_auth)):
    """
    Get user statistics (transaction counts, amounts, VIP level).
    """
    try:
        user_id = user_data.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user data")
        
        user_dict = UserRepository.get_user(user_id)
        if not user_dict:
            raise HTTPException(status_code=404, detail="User not found")
        
        total_trans = TransactionRepository.get_transaction_count(user_id)
        total_receive = TransactionRepository.get_transaction_count(user_id, "receive")
        total_pay = TransactionRepository.get_transaction_count(user_id, "pay")
        total_amount = float(user_dict.get('total_amount', 0))
        vip_level = user_dict.get('vip_level', 0)
        
        return StatisticsResponse(
            total_transactions=total_trans,
            total_receive=total_receive,
            total_pay=total_pay,
            total_amount=total_amount,
            vip_level=vip_level
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 10,
    offset: int = 0,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    user_data: dict = Depends(verify_auth)
):
    """
    Get user's transaction history.
    """
    try:
        user_id = user_data.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user data")
        
        transactions = TransactionRepository.get_user_transactions(
            user_id=user_id,
            limit=limit,
            offset=offset,
            transaction_type=transaction_type,
            status=status
        )
        
        result = []
        for t in transactions:
            result.append(TransactionResponse(
                transaction_id=t['transaction_id'],
                order_id=t['order_id'],
                transaction_type=t['transaction_type'],
                payment_channel=t['payment_channel'],
                amount=float(t['amount']),
                fee=float(t['fee']),
                actual_amount=float(t['actual_amount']),
                currency=t['currency'],
                status=t['status'],
                description=t.get('description'),
                created_at=t.get('created_at', ''),
                paid_at=t.get('paid_at'),
                expired_at=t.get('expired_at')
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/rates")
async def get_rates(user_data: dict = Depends(verify_auth)):
    """
    Get current exchange rates and fee structure.
    """
    try:
        user_id = user_data.get('id')
        vip_level = 0
        
        if user_id:
            user_dict = UserRepository.get_user(user_id)
            if user_dict:
                vip_level = user_dict.get('vip_level', 0)
        
        # Get rates for user's VIP level
        rates = RateRepository.get_rate_by_channel_and_vip('alipay', vip_level)
        
        return {
            "alipay": {
                "fee_rate": rates.get('fee_rate', 0) if rates else 0,
                "min_amount": rates.get('min_amount', 0) if rates else 0,
                "max_amount": rates.get('max_amount', 0) if rates else 0,
            },
            "wechat": {
                "fee_rate": rates.get('fee_rate', 0) if rates else 0,
                "min_amount": rates.get('min_amount', 0) if rates else 0,
                "max_amount": rates.get('max_amount', 0) if rates else 0,
            },
            "vip_level": vip_level
        }
        
    except Exception as e:
        logger.error(f"Error getting rates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/videos/wechat")
async def get_wechat_video_url():
    """
    Get WeChat video URL from Telegram channel.
    Returns the download URL for the latest WeChat video.
    """
    try:
        # Get video config from database
        video_config = VideoRepository.get_video_config_by_type("wechat")
        
        if not video_config:
            raise HTTPException(status_code=404, detail="WeChat video not configured")
        
        file_id = video_config['file_id']
        
        # Get file info from Telegram Bot API
        async with httpx.AsyncClient() as client:
            bot_token = Config.BOT_TOKEN
            response = await client.get(
                f"https://api.telegram.org/bot{bot_token}/getFile",
                params={"file_id": file_id}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get file info: {response.text}")
                raise HTTPException(status_code=500, detail="Failed to get video file info")
            
            file_info = response.json()
            if not file_info.get('ok'):
                logger.error(f"Telegram API error: {file_info}")
                raise HTTPException(status_code=500, detail="Telegram API error")
            
            file_path = file_info['result']['file_path']
            video_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            
            return {
                "url": video_url,
                "file_id": file_id,
                "file_path": file_path,
                "updated_at": video_config.get('updated_at')
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting WeChat video URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/videos/alipay")
async def get_alipay_video_url():
    """
    Get Alipay video URL from Telegram channel.
    Returns the download URL for the latest Alipay video.
    """
    try:
        # Get video config from database
        video_config = VideoRepository.get_video_config_by_type("alipay")
        
        if not video_config:
            raise HTTPException(status_code=404, detail="Alipay video not configured")
        
        file_id = video_config['file_id']
        
        # Get file info from Telegram Bot API
        async with httpx.AsyncClient() as client:
            bot_token = Config.BOT_TOKEN
            response = await client.get(
                f"https://api.telegram.org/bot{bot_token}/getFile",
                params={"file_id": file_id}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get file info: {response.text}")
                raise HTTPException(status_code=500, detail="Failed to get video file info")
            
            file_info = response.json()
            if not file_info.get('ok'):
                logger.error(f"Telegram API error: {file_info}")
                raise HTTPException(status_code=500, detail="Telegram API error")
            
            file_path = file_info['result']['file_path']
            video_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            
            return {
                "url": video_url,
                "file_id": file_id,
                "file_path": file_path,
                "updated_at": video_config.get('updated_at')
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Alipay video URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/binance/p2p")
async def get_binance_p2p_data(
    payment_method: str = "alipay",
    rows: int = 10,
    page: int = 1
):
    """
    Get Binance P2P merchant leaderboard data.
    
    Args:
        payment_method: Payment method ("alipay", "wechat", "bank")
        rows: Number of merchants per page (default: 10)
        page: Page number (default: 1)
        user_data: Authenticated user data (from verify_auth dependency)
        
    Returns:
        Dictionary with merchant leaderboard data
    """
    try:
        # Try to import P2P service from botB or botA
        leaderboard_data = None
        try:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent
            
            # Try botB first
            botb_path = project_root / "botB" / "services" / "p2p_leaderboard_service.py"
            if botb_path.exists():
                sys.path.insert(0, str(project_root / "botB"))
                from services.p2p_leaderboard_service import get_p2p_leaderboard
                leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=rows, page=page)
            else:
                # Fallback to botA
                bota_path = project_root / "botA" / "services" / "p2p_leaderboard_service.py"
                if bota_path.exists():
                    sys.path.insert(0, str(project_root / "botA"))
                    from services.p2p_leaderboard_service import get_p2p_leaderboard
                    leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=rows, page=page)
        except (ImportError, Exception) as e:
            logger.warning(f"Could not import p2p_leaderboard_service: {e}, using inline implementation")
        
        # If import failed or returned None, use inline implementation
        if not leaderboard_data:
            leaderboard_data = get_p2p_leaderboard_inline(payment_method, rows, page)
        
        if not leaderboard_data:
            raise HTTPException(status_code=500, detail="Failed to fetch Binance P2P data")
        
        return leaderboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Binance P2P data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def get_p2p_leaderboard_inline(payment_method: str = "alipay", rows: int = 10, page: int = 1):
    """
    Inline implementation of Binance P2P leaderboard fetch (fallback if service import fails).
    """
    BINANCE_P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    PAYMENT_METHOD_MAP = {
        "bank": ["BANK"],
        "alipay": ["ALIPAY"],
        "wechat": ["WECHAT"],
    }
    PAYMENT_METHOD_LABELS = {
        "bank": "银行卡",
        "alipay": "支付宝",
        "wechat": "微信",
    }
    
    try:
        pay_types = PAYMENT_METHOD_MAP.get(payment_method.lower(), ["ALIPAY"])
        payload = {
            "page": page,
            "rows": rows,
            "payTypes": pay_types,
            "asset": "USDT",
            "tradeType": "BUY",
            "fiat": "CNY",
            "countries": [],
            "proMerchantAds": False,
            "shieldMerchantAds": False
        }
        
        response = requests.post(
            BINANCE_P2P_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "000000" or not data.get("success"):
            logger.error(f"Binance P2P API error: {data}")
            return None
        
        merchants_data = data.get("data", [])
        merchants = []
        
        for idx, item in enumerate(merchants_data[:rows], 1):
            adv_data = item.get("adv", {})
            advertiser_data = item.get("advertiser", {})
            
            merchant_name = advertiser_data.get("nickName", "Unknown")
            price_str = adv_data.get("price", "0")
            price = float(price_str) if price_str else 0.0
            
            min_amount_str = adv_data.get("minSingleTransAmount", "0")
            max_amount_str = adv_data.get("maxSingleTransAmount", "0")
            min_amount = float(min_amount_str) if min_amount_str else 0.0
            max_amount = float(max_amount_str) if max_amount_str else 0.0
            
            # Get trade count (try multiple fields)
            trade_count = advertiser_data.get("monthFinishCount", 0) or advertiser_data.get("monthOrderCount", 0) or 0
            finish_rate = advertiser_data.get("monthFinishRate", 0.0) or 0.0
            
            merchants.append({
                "rank": idx,
                "price": price,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "merchant_name": merchant_name,
                "trade_count": trade_count,
                "finish_rate": finish_rate,
            })
        
        # Calculate market stats
        prices = [m["price"] for m in merchants if m["price"] > 0]
        market_stats = {
            "min_price": min(prices) if prices else 0.0,
            "max_price": max(prices) if prices else 0.0,
            "avg_price": sum(prices) / len(prices) if prices else 0.0,
            "total_trades": len(merchants),
            "merchant_count": len(merchants),
        }
        
        return {
            "merchants": merchants,
            "payment_method": payment_method,
            "payment_label": PAYMENT_METHOD_LABELS.get(payment_method, payment_method),
            "total": len(merchants),
            "page": page,
            "market_stats": market_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching Binance P2P data (inline): {e}", exc_info=True)
        return None


class CustomerServiceAssignRequest(BaseModel):
    """Request model for customer service assignment"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class CustomerServiceAssignResponse(BaseModel):
    """Response model for customer service assignment"""
    service_account: str
    assignment_method: str
    success: bool
    message: Optional[str] = None


@app.post("/api/customer-service/assign", response_model=CustomerServiceAssignResponse)
async def assign_customer_service(
    request: Optional[CustomerServiceAssignRequest] = None,
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
):
    """
    Assign a customer service account to a user (for MiniApp).
    
    Uses the same smart allocation logic as Bot A and Bot B.
    Authentication is optional - if initData is provided, it will be verified.
    Otherwise, user_id and username from request body will be used.
    """
    try:
        # Try to get user info from authenticated initData first
        user_data = None
        if x_telegram_init_data:
            try:
                if verify_telegram_init_data(x_telegram_init_data, Config.BOT_TOKEN):
                    user_data = parse_init_data(x_telegram_init_data)
            except Exception as e:
                logger.warning(f"Failed to verify initData, using request body: {e}")
        
        # Get user info from auth or request body
        if user_data:
            # Use authenticated user data (preferred)
            user_id = user_data.get('id')
            username = user_data.get('username')
        elif request:
            # Use request body data
            user_id = request.user_id
            username = request.username
        else:
            # No data provided
            user_id = None
            username = None
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if not username:
            username = f"user_{user_id}"
        
        # Import shared customer service service
        # Try to import from root services first, then from botB
        try:
            from services.customer_service_service import customer_service
        except ImportError:
            # Fallback: import from botB
            import sys
            from pathlib import Path
            botb_path = Path(__file__).parent / "botB"
            if botb_path.exists():
                sys.path.insert(0, str(botb_path))
            from services.customer_service_service import customer_service
        
        # Get assignment strategy from settings
        if hasattr(customer_service, 'get_assignment_strategy'):
            assignment_method = customer_service.get_assignment_strategy()
        else:
            # Fallback: try to get from database directly
            try:
                from botB.database import db
                all_settings = db.get_all_settings()
                assignment_method = all_settings.get('customer_service_strategy', 'round_robin')
            except:
                assignment_method = 'round_robin'  # Default fallback
        
        # Assign customer service account
        service_account = customer_service.assign_service(
            user_id=user_id,
            username=username,
            method=assignment_method
        )
        
        if service_account:
            logger.info(f"Assigned customer service @{service_account} to user {user_id} via API")
            return CustomerServiceAssignResponse(
                service_account=service_account,
                assignment_method=assignment_method,
                success=True,
                message=f"Assigned to @{service_account}"
            )
        else:
            # No available customer service - return error
            logger.warning(f"No available customer service for user {user_id} via API")
            return CustomerServiceAssignResponse(
                service_account="",
                assignment_method=assignment_method,
                success=False,
                message="No available customer service account"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning customer service via API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

