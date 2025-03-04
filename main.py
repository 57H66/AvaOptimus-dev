import sys
import os
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

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).post_init(set_bot_commands).build()

    # 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", handle_menu_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(button))

    # 启动轮询
    application.run_polling()