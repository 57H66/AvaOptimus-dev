import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from info_fetcher import get_token_info, get_funding_rate_and_open_interest,get_top_20_tokens_by_volume
from menu_handler import menu

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 封装创建返回菜单内联键盘的函数
def create_back_to_menu_keyboard():
    keyboard = [[InlineKeyboardButton("返回菜单", callback_data='menu')]]
    return InlineKeyboardMarkup(keyboard)

# 封装查询处理逻辑
async def handle_query(update, context, query_func, mode_key):
    user_input = update.message.text
    if user_input.lower() == "menu":
        await menu(update, context)
        context.chat_data[mode_key] = False
        return
    try:
        token_symbol = user_input.upper()
        trading_pair = f"{token_symbol}USDT"
        result = await query_func(trading_pair)
        reply_markup = create_back_to_menu_keyboard()
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=result,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logging.error(f"查询 {trading_pair} 信息时出错: {e}")
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="查询过程中出现错误，请稍后再试。",
            reply_markup=create_back_to_menu_keyboard()
        )
     

async def echo(update, context):
    user_input = update.message.text
    in_query_mode = context.chat_data.get("in_token_query_mode", False)
    in_funding_rate_mode = context.chat_data.get("in_funding_rate_mode", False)

    if in_query_mode:
        await handle_query(update, context, get_token_info, "in_token_query_mode")
        return

    if in_funding_rate_mode:
        await handle_query(update, context, get_funding_rate_and_open_interest, "in_funding_rate_mode")
        return

    if user_input == "代币查询":
        reply_markup = create_back_to_menu_keyboard()
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="请输入你想要查询的代币名称（如 BTC、ETH 等）：",
            reply_markup=reply_markup
        )
        context.chat_data["in_token_query_mode"] = True

    elif user_input == "热门代币":
        # 获取当日交易量前 20 的代币
        popular_tokens =  get_top_20_tokens_by_volume()

        # 创建包含 "返回菜单" 按钮的内联键盘
        reply_markup = create_back_to_menu_keyboard()
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"当日交易量前 20 的代币：\n{popular_tokens}",
            reply_markup=reply_markup
        )
        
    elif user_input == "帮助":
        reply_markup = create_back_to_menu_keyboard()
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="欢迎使用AvaOptimus机器人！\n"
                 "你可以选择以下功能：\n"
                 "- 代币查询：输入代币名称查询最新价格\n"
                 "- 热门代币：查看热门代币列表\n"
                 "- 帮助：获取帮助信息\n"
                 "- 代币合约持仓与费率：查询代币合约的持仓与费率信息",
            reply_markup=reply_markup
        )

    elif user_input == "代币合约持仓与费率":
        reply_markup = create_back_to_menu_keyboard()
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="请输入你想要查询合约信息的代币名称（如 BTC、ETH 等）：",
            reply_markup=reply_markup
        )
        context.chat_data["in_funding_rate_mode"] = True

    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"你发送了：{user_input}"
        )