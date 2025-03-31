import os
import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = int(os.environ['ADMIN_ID'])

# Создание базы
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang TEXT DEFAULT 'ru')''')
conn.commit()
conn.close()

def set_lang(user_id, lang):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
    conn.commit()
    conn.close()

def get_lang(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'ru'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    set_lang(user_id, 'ru')

    keyboard = [[
        InlineKeyboardButton("📊 Информация о рейке", callback_data='rake_info')
    ], [
        InlineKeyboardButton("🎁 Бонус за друга", callback_data='friend_bonus')
    ], [
        InlineKeyboardButton("🆘 Поддержка", callback_data='support')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в Rogue Royals Poker Club!", reply_markup=reply_markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'rake_info':
        await query.edit_message_text("♠️ Рейк: 60% игрокам. Выплаты каждую неделю!")
    elif query.data == 'friend_bonus':
        await query.edit_message_text("💰 Пригласи друга и получи $10 к пополнению!")
    elif query.data == 'support':
        await query.edit_message_text("📞 Напишите @RogueRoyals для связи с менеджером.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Недостаточно прав!")
        return

    message = " ".join(context.args)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    for user in users:
        try:
            await context.bot.send_message(chat_id=user[0], text=message)
        except:
            pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(CommandHandler('broadcast', broadcast))
    print("Бот запущен!")
    app.run_polling()
