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
from services.p2p_leaderboard_service import get_p2p_leaderboard
import httpx

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
async def get_binance_p2p(
    payment_method: str = "alipay",
    rows: int = 10,
    page: int = 1
):
    """
    Get P2P merchant leaderboard from OKX C2C (primary) or Binance P2P (fallback).
    Only uses Alipay payment method for price calculation.
    
    Args:
        payment_method: Payment method ("bank", "alipay", "wechat")
        rows: Number of merchants to fetch
        page: Page number (for Binance fallback)
        
    Returns:
        Dictionary with merchant data
    """
    try:
        # Get leaderboard data (OKX primary, Binance fallback)
        leaderboard_data = get_p2p_leaderboard(
            payment_method=payment_method,
            rows=rows,
            page=page
        )
        
        if not leaderboard_data:
            raise HTTPException(status_code=500, detail="Failed to fetch P2P leaderboard data")
        
        # Format response for MiniApp
        merchants = []
        for merchant in leaderboard_data.get('merchants', []):
            merchants.append({
                'rank': merchant.get('rank', 0),
                'price': merchant.get('price', 0),
                'min_amount': merchant.get('min_amount', 0),
                'max_amount': merchant.get('max_amount', 0),
                'merchant_name': merchant.get('merchant_name', 'Unknown'),
                'trade_count': merchant.get('trade_count', 0),
                'finish_rate': merchant.get('finish_rate', 0)
            })
        
        return {
            'merchants': merchants,
            'payment_method': leaderboard_data.get('payment_method', payment_method),
            'payment_label': leaderboard_data.get('payment_label', '支付宝'),
            'total': leaderboard_data.get('total', len(merchants)),
            'page': leaderboard_data.get('page', page),
            'market_stats': leaderboard_data.get('market_stats', {
                'min_price': 0,
                'max_price': 0,
                'avg_price': 0,
                'total_trades': 0,
                'merchant_count': 0
            })
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting P2P leaderboard: {e}", exc_info=True)
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

