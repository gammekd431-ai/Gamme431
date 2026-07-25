import time
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Configuration
API_TOKEN = '8626785598:AAGuwTiweoKL5eOrUqYE04sb_ta3QSIaKfk'  # Bot Token kee asitti galchi
ADMIN_ID = 365353683
WEB_APP_URL = 'https://gamme-430.github.io/DaimondLottery431/'
FIREBASE_URL = 'https://diamond-lottery-78180-default-rtdb.asia-southeast1.firebasedatabase.app/'

bot = telebot.TeleBot(API_TOKEN)

# ----------------- FIREBASE REST API HELPER -----------------
def db_get(path):
    try:
        r = requests.get(f"{FIREBASE_URL}{path}.json", timeout=5)
        return r.json()
    except Exception as e:
        print(f"DB Get Error: {e}")
        return None

def db_set(path, data):
    try:
        r = requests.put(f"{FIREBASE_URL}{path}.json", json=data, timeout=5)
        return r.json()
    except Exception as e:
        print(f"DB Set Error: {e}")
        return None

# ----------------- KEYBOARDS -----------------
def admin_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Waliigala Stats", callback_data="admin_stats"),
        InlineKeyboardButton("🎮 Qindaa'ina Taphaa", callback_data="admin_games"),
        InlineKeyboardButton("👤 Bulchiinsa Users", callback_data="admin_users"),
        InlineKeyboardButton("💰 Kafaltii & Baasii", callback_data="admin_finance"),
        InlineKeyboardButton("📢 Ergaa Waliigalaa", callback_data="admin_broadcast")
    )
    return markup

def admin_game_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💵 Gatii Taphichaa (Bet)", callback_data="game_bet"),
        InlineKeyboardButton("🛑 Taphicha Dhaabi/Jalqabi", callback_data="game_toggle"),
        InlineKeyboardButton("🔙 Gara Menu Jalqabaa", callback_data="back_to_main")
    )
    return markup

# ----------------- HANDLERS -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or "No Username"

    user_data = db_get(f'users/{user_id}')
    if not user_data:
        db_set(f'users/{user_id}', {
            'balance': 0,
            'username': username,
            'first_name': first_name,
            'joined_at': int(time.time())
        })

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎮 Diamond Lottery Taphaadhu", web_app=WebAppInfo(url=WEB_APP_URL))
    )

    bot.send_message(
        message.chat.id,
        f"👋 Nagaan dhuftan **{first_name}**!\n\n"
        "💎 **Diamond Lottery** irratti carraa keessan yaaluuf cuqaasaa gadii tuqaa:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "👋 **Diamond Lottery Admin Panel!**",
            reply_markup=admin_main_menu()
        )
    else:
        bot.send_message(message.chat.id, "⚠️ Mirga hin qabdu!")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⚠️ Mirga hin qabdu!", show_alert=True)
        return

    if call.data == "back_to_main":
        bot.edit_message_text("Filannoo keessan cuqaasaa:", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())

    elif call.data == "admin_games":
        bot.edit_message_text("⚙️ **Qindaa'ina Taphaa:**", call.message.chat.id, call.message.message_id, reply_markup=admin_game_menu(), parse_mode="Markdown")

    elif call.data == "admin_stats":
        users_data = db_get('users') or {}
        total_users = len(users_data)
        current_bet = db_get('settings/bet_amount') or 20
        status = db_get('settings/game_status') or "Bifaan Jira"

        stats_msg = f"📊 **Waliigala Data:**\n• Users: {total_users}\n• Bet Ammaa: {current_bet} ETB\n• Status: {status}"
        bot.send_message(call.message.chat.id, stats_msg, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

if __name__ == '__main__':
    print("🚀 Botiin Pydroid 3 irratti ka'eera...")
    bot.infinity_polling()
