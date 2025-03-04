from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from info_fetcher import get_top_20_tokens_by_volume
async def menu(update, context):
    # 创建菜单的内联键盘
    keyboard = [
        [InlineKeyboardButton("代币查询", callback_data='token_query')],
        [InlineKeyboardButton("热门代币", callback_data='popular_tokens')],
        [InlineKeyboardButton("代币合约持仓与费率",callback_data='funding_rate')],
        [InlineKeyboardButton("帮助", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if hasattr(update, 'message'):
        chat_id = update.message.chat_id
    else:
        chat_id = update.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="请选择功能",
        reply_markup=reply_markup
    )
    context.chat_data["in_token_query_mode"] = False

async def button(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'menu':
        await menu(query.message, context)
    elif query.data == 'token_query':
        # 创建包含 "返回菜单" 按钮的内联键盘
        keyboard = [[InlineKeyboardButton("返回菜单", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="请输入你想要查询的代币名称（如 BTC、ETH 等）：",
            reply_markup=reply_markup
        )
        context.chat_data["in_token_query_mode"] = True
        
    elif query.data == 'popular_tokens':
         # 获取当日交易量前 20 的代币
        popular_tokens = get_top_20_tokens_by_volume()
        # 创建包含 "返回菜单" 按钮的内联键盘
        keyboard = [[InlineKeyboardButton("返回菜单", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"当日交易量前 20 的代币：\n{popular_tokens}",
            reply_markup=reply_markup
        )
    elif query.data == 'funding_rate':
        # 创建包含 "返回菜单" 按钮的内联键盘
        keyboard = [[InlineKeyboardButton("返回菜单", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="请输入你想要查询合约信息的代币名称（如 BTC、ETH 等）：",
            reply_markup=reply_markup
        )
        context.chat_data["in_funding_rate_mode"] = True
        
    elif query.data == 'help':
        # 创建包含 "返回菜单" 按钮的内联键盘
        keyboard = [[InlineKeyboardButton("返回菜单", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="欢迎使用代币查询机器人！\n"
                 "你可以选择以下功能：\n"
                 "- 代币查询：输入代币名称查询最新价格\n"
                 "- 热门代币：查看热门代币列表\n"
                 "- 帮助：获取帮助信息",
            reply_markup=reply_markup
        )

async def set_bot_commands(application):
    commands = [
        BotCommand("menu", "返回菜单"),
        BotCommand("btc", "BTC 现货合约分析"),
        BotCommand("eth","ETH 现货合约分析")
        ]
    await application.bot.set_my_commands(commands)