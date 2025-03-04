from menu_handler import menu

async def start(update, context):
    await menu(update, context)

async def handle_menu_command(update, context):
    await menu(update, context)