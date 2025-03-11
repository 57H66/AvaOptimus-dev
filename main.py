import sys
import os
import asyncio
import aiohttp  # 导入 aiohttp 库
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 确保相关模块所在目录在模块搜索路径中
sys.path.append(current_dir)


from config import TOKEN
from command_handler import start, handle_menu_command
from message_handler import echo
from menu_handler import button, set_bot_commands
from data_storage_fetcher import (
    fetch_and_store_kline_data,
    fetch_and_store_realtime_price,
    fetch_and_store_24h_price_change,
    fetch_and_store_contract_data
)
from db_utils import init_db
# 定义需要监控的代币列表
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

async def data_storage_task():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for symbol in SYMBOLS:
            tasks.append(fetch_and_store_kline_data(session, symbol))
            tasks.append(fetch_and_store_realtime_price(session, symbol))
            tasks.append(fetch_and_store_24h_price_change(session, symbol))
            tasks.append(fetch_and_store_contract_data(session, symbol))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    init_db()  # 调用 init_db 函数初始化数据库
    application = ApplicationBuilder().token(TOKEN).post_init(set_bot_commands).build()

    # 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", handle_menu_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(button))

    # 创建事件循环
    loop = asyncio.get_event_loop()

    # 启动数据存储任务
    data_task = loop.create_task(data_storage_task())

    try:
        # 启动 Telegram Bot 轮询
        loop.run_until_complete(application.run_polling())
    except KeyboardInterrupt:
        # 处理 Ctrl+C 中断
        data_task.cancel()
        try:
            loop.run_until_complete(data_task)
        except asyncio.CancelledError:
            pass
    finally:
        loop.close()