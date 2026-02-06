# main.py
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import start, contact_handler, button_handler, admin_command, text_handler, set_application

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from config import BOT_TOKEN

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Передаем application в handlers для уведомлений
    set_application(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    
    # Обработчик текста для админов (специальные команды)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, text_handler))
    
    # Обработчик callback-кнопок
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == '__main__':
    from database import init_db
    init_db()
    main()