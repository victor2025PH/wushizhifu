"""
Referral/Sharing activity handlers
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import get_main_keyboard
from database.referral_repository import ReferralRepository
from database.user_repository import UserRepository
from database.admin_repository import AdminRepository
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown, format_separator

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "referral_main")
async def callback_referral_main(callback: CallbackQuery):
    """Handle referral main menu"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        from config import Config
        
        user_id = callback.from_user.id
        
        # Get referral stats
        stats = ReferralRepository.get_referral_stats(user_id)
        
        # Get current month ranking
        current_month = datetime.now().strftime("%Y-%m")
        rankings = ReferralRepository.get_monthly_ranking(current_month, 20)
        
        user_rank = None
        for idx, rank in enumerate(rankings, 1):
            if rank['user_id'] == user_id:
                user_rank = idx
                break
        
        separator = format_separator(30)
        total_invites_str = format_number_markdown(stats['total_invites'])
        successful_invites_str = format_number_markdown(stats['successful_invites'])
        total_rewards_str = format_amount_markdown(stats['total_rewards'], currency="USDT")
        lottery_entries_str = format_number_markdown(stats['lottery_entries'])
        rank_text = f"第 {user_rank} 名" if user_rank else "未上榜"
        
        text = (
            f"{separator}\n"
            f"  *🎁 分享有礼 活动中心*\n"
            f"{separator}\n\n"
            
            f"*💎 我的分享数据*\n"
            f"{separator}\n"
            f"📊 *总邀请*：{total_invites_str} 人\n"
            f"✅ *成功邀请*：{successful_invites_str} 人\n"
            f"💰 *累计奖励*：{total_rewards_str}\n"
            f"🎲 *抽奖次数*：{lottery_entries_str} 次\n"
            f"🏆 *本月排名*：{escape_markdown_v2(rank_text)}\n\n"
            
            f"*🎯 活动规则*\n"
            f"{separator}\n"
            f"📱 *邀请好友*：10 USDT/人\n"
            f"💸 *交易分红*：交易额 1\\%（最高 100 USDT）\n"
            f"🎁 *好友红包*：首次交易送 5 USDT\n"
            f"🎲 *每 5 人*可抽奖\n"
            f"🏆 *月度前三*：999/888/777 USDT\n\n"
            
            f"💡 *邀请奖励说明*\n"
            f"✅ 好友注册：\\+10 USDT\n"
            f"✅ 好友首次交易：\\+交易额 1\\%（最高 100 USDT）\n"
            f"✅ 好友获得：首次交易 5 USDT 红包\n"
            f"✅ 邀请 5 人：获得 1 次抽奖机会"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 邀请好友", callback_data="referral_invite"),
                InlineKeyboardButton(text="💰 我的奖励", callback_data="referral_rewards")
            ],
            [
                InlineKeyboardButton(text="🏆 排行榜", callback_data="referral_ranking"),
                InlineKeyboardButton(text="🎲 抽奖", callback_data="referral_lottery")
            ],
            [
                InlineKeyboardButton(text="🔙 返回主菜单", callback_data="main_menu")
            ]
        ])
        
        try:
            await callback.message.edit_text(
                text=text,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                raise
            await callback.answer("✅ 数据已是最新", show_alert=False)
            return
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_referral_main: {e}", exc_info=True)
        await callback.answer("❌ 获取分享活动信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "referral_invite")
async def callback_referral_invite(callback: CallbackQuery):
    """Handle invite friend page"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        from config import Config
        
        user_id = callback.from_user.id
        
        # Get or create referral code
        code = ReferralRepository.get_or_create_referral_code(user_id)
        code_escaped = escape_markdown_v2(code)
        
        # Generate share link
        bot_username = (await callback.bot.get_me()).username
        share_link = f"https://t.me/{bot_username}?start=ref_{code}"
        link_escaped = escape_markdown_v2(share_link)
        
        separator = format_separator(30)
        
        text = (
            f"{separator}\n"
            f"  *📱 邀请好友赚奖励*\n"
            f"{separator}\n\n"
            
            f"*🆔 我的推荐码*\n"
            f"{separator}\n"
            f"复制推荐码：`{code_escaped}`\n\n"
            
            f"*🔗 分享链接*\n"
            f"{separator}\n"
            f"`{link_escaped}`\n\n"
            
            f"点击下方按钮快速分享给好友\n\n"
            
            f"{separator}\n"
            f"*💡 邀请奖励说明*\n"
            f"{separator}\n"
            f"✅ *好友注册*：\\+10 USDT\n"
            f"✅ *好友首次交易*：\\+交易额 1\\%（最高 100 USDT）\n"
            f"✅ *好友获得*：首次交易 5 USDT 红包\n"
            f"✅ *邀请 5 人*：获得 1 次抽奖机会"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 分享给好友",
                    url=f"https://t.me/share/url?url={share_link}&text=🎁%20伍拾支付%20分享有礼！邀请您使用数字资产支付服务，首次交易送5%20USDT红包！"
                )
            ],
            [
                InlineKeyboardButton(text="📋 复制链接", callback_data=f"copy_link_{code}"),
                InlineKeyboardButton(text="🔙 返回", callback_data="referral_main")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_referral_invite: {e}", exc_info=True)
        await callback.answer("❌ 获取邀请信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "referral_rewards")
async def callback_referral_rewards(callback: CallbackQuery):
    """Handle rewards record page"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        
        # Get reward records
        rewards = ReferralRepository.get_user_rewards(user_id, limit=10)
        
        # Calculate totals
        total_rewards = sum(float(r['amount']) for r in rewards if r['status'] == 'paid')
        pending_rewards = sum(float(r['amount']) for r in rewards if r['status'] == 'pending')
        
        separator = format_separator(30)
        total_str = format_amount_markdown(total_rewards, currency="USDT")
        pending_str = format_amount_markdown(pending_rewards, currency="USDT")
        paid_str = format_amount_markdown(total_rewards - pending_rewards, currency="USDT")
        
        text = (
            f"{separator}\n"
            f"  *💰 我的奖励记录*\n"
            f"{separator}\n\n"
            
            f"*💎 奖励统计*\n"
            f"{separator}\n"
            f"💰 *累计奖励*：{total_str}\n"
            f"💳 *待发放*：{pending_str}\n"
            f"✅ *已发放*：{paid_str}\n\n"
            
            f"*📋 最近奖励*\n"
            f"{separator}\n"
        )
        
        if not rewards:
            text += "暂无奖励记录\n\n开始邀请好友获得奖励吧！"
        else:
            for reward in rewards[:10]:
                status_icon = "✅" if reward['status'] == 'paid' else "⏳"
                amount_str = format_amount_markdown(float(reward['amount']), currency="USDT")
                desc_escaped = escape_markdown_v2(reward.get('description', '奖励'))
                date_str = escape_markdown_v2(str(reward['created_at'])[:10])
                
                text += (
                    f"{status_icon} \\+{amount_str} \\- {desc_escaped}\n"
                    f"   {date_str}\n\n"
                )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回", callback_data="referral_main")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_referral_rewards: {e}", exc_info=True)
        await callback.answer("❌ 获取奖励记录失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "referral_ranking")
async def callback_referral_ranking(callback: CallbackQuery):
    """Handle monthly ranking page"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        current_month = datetime.now().strftime("%Y-%m")
        
        # Get rankings
        rankings = ReferralRepository.get_monthly_ranking(current_month, 10)
        
        # Calculate days until month end
        now = datetime.now()
        if now.month == 12:
            month_end = datetime(now.year + 1, 1, 1)
        else:
            month_end = datetime(now.year, now.month + 1, 1)
        days_left = (month_end - now).days
        
        separator = format_separator(30)
        month_text = escape_markdown_v2(current_month)
        days_str = format_number_markdown(days_left)
        
        text = (
            f"{separator}\n"
            f"  *🏆 月度邀请排行榜*\n"
            f"{separator}\n\n"
            
            f"📅 {month_text}\n\n"
        )
        
        if not rankings:
            text += "暂无排名数据\n\n本月还没有人参与分享活动"
        else:
            # Top 3 with special emojis
            for idx, rank in enumerate(rankings[:3], 1):
                username = rank.get('username') or f"用户{rank['user_id']}"
                username_escaped = escape_markdown_v2(username)
                invite_count_str = format_number_markdown(rank['invite_count'])
                reward_str = format_amount_markdown(float(rank.get('reward_amount', 0)), currency="USDT")
                
                if idx == 1:
                    text += f"🥇 *第 1 名*：{username_escaped}\n"
                    text += f"   邀请：{invite_count_str} 人 \\| 奖励：{reward_str}\n\n"
                elif idx == 2:
                    text += f"🥈 *第 2 名*：{username_escaped}\n"
                    text += f"   邀请：{invite_count_str} 人 \\| 奖励：{reward_str}\n\n"
                elif idx == 3:
                    text += f"🥉 *第 3 名*：{username_escaped}\n"
                    text += f"   邀请：{invite_count_str} 人 \\| 奖励：{reward_str}\n\n"
            
            # Rest of rankings
            for rank in rankings[3:10]:
                username = rank.get('username') or f"用户{rank['user_id']}"
                username_escaped = escape_markdown_v2(username)
                invite_count_str = format_number_markdown(rank['invite_count'])
                rank_num = rankings.index(rank) + 1
                
                text += (
                    f"{format_number_markdown(rank_num)}️⃣ *第 {rank_num} 名*：{username_escaped} \\- "
                    f"邀请：{invite_count_str} 人\n"
                )
            
            # User's rank
            user_rank = None
            for idx, rank in enumerate(rankings, 1):
                if rank['user_id'] == user_id:
                    user_rank = idx
                    break
            
            if user_rank:
                user_invites = next(r['invite_count'] for r in rankings if r['user_id'] == user_id)
                user_invites_str = format_number_markdown(user_invites)
                text += f"\n🏆 *您的排名*：第 {user_rank} 名\n"
                text += f"   邀请：{user_invites_str} 人"
        
        text += (
            f"\n\n{separator}\n"
            f"⏰ *距离结算*：还有 {days_str} 天\n"
            f"   次月 5 日前发放奖励"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回", callback_data="referral_main")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_referral_ranking: {e}", exc_info=True)
        await callback.answer("❌ 获取排行榜失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "referral_lottery")
async def callback_referral_lottery(callback: CallbackQuery):
    """Handle lottery page"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        
        # Get lottery entries
        stats = ReferralRepository.get_referral_stats(user_id)
        lottery_entries = stats['lottery_entries']
        
        separator = format_separator(30)
        entries_str = format_number_markdown(lottery_entries)
        
        text = (
            f"{separator}\n"
            f"  *🎲 幸运抽奖*\n"
            f"{separator}\n\n"
            
            f"*🎁 奖品池*\n"
            f"{separator}\n"
            f"🏆 *一等奖*：500 USDT \\(10\\%\\)\n"
            f"🥈 *二等奖*：100 USDT \\(20\\%\\)\n"
            f"🥉 *三等奖*：50 USDT \\(30\\%\\)\n"
            f"🎁 *幸运奖*：10 USDT \\(40\\%\\)\n\n"
            
            f"*🎯 我的抽奖*\n"
            f"{separator}\n"
            f"剩余次数：{entries_str} 次\n\n"
        )
        
        if lottery_entries <= 0:
            text += "❌ 暂无抽奖次数\n\n每邀请 5 位好友完成首次交易，即可获得 1 次抽奖机会！"
        else:
            text += "点击下方按钮开始抽奖！"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if lottery_entries > 0:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="🎲 开始抽奖", callback_data="referral_lottery_draw")
            ])
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="🔙 返回", callback_data="referral_main")
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_referral_lottery: {e}", exc_info=True)
        await callback.answer("❌ 获取抽奖信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "referral_lottery_draw")
async def callback_referral_lottery_draw(callback: CallbackQuery):
    """Handle lottery draw"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        
        # Draw lottery
        result = ReferralRepository.draw_lottery(user_id)
        
        if not result:
            await callback.answer("❌ 抽奖次数不足", show_alert=True)
            return
        
        prize_level = result['prize_level']
        prize_amount = result['prize_amount']
        
        prize_names = {
            1: "🏆 一等奖",
            2: "🥈 二等奖",
            3: "🥉 三等奖",
            4: "🎁 幸运奖"
        }
        
        prize_name = prize_names.get(prize_level, "🎁 奖品")
        prize_amount_str = format_amount_markdown(prize_amount, currency="USDT")
        
        text = (
            f"*🎉 恭喜中奖！*\n\n"
            f"{prize_name}\n"
            f"奖励：{prize_amount_str}\n\n"
            f"奖励已自动发放到您的账户！"
        )
        
        await callback.answer(text, show_alert=True)
        
        # Refresh lottery page
        await callback_referral_lottery(callback)
        
    except Exception as e:
        logger.error(f"Error in callback_referral_lottery_draw: {e}", exc_info=True)
        await callback.answer("❌ 抽奖失败，请稍后再试", show_alert=True)

