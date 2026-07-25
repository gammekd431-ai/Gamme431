import threading
import random
import telebot
import os
import firebase_admin
from firebase_admin import credentials, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# --- FIREBASE SIRREESSUU ---
# File-icha 'serviceAccountKey.json' jedhiitii folder-ii kee keessatti kaa'i.
# Koodiin kun file-icha folder-ii kee keessaa ofumaan dubbisa.
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://diamond-lottery-78180-default-rtdb.asia-southeast1.firebasedatabase.app'
})

API_TOKEN = '8626785598:AAEVr2JPv58Cw9V8QrznuhxJY5lb1ch8Dcg'
ADMIN_ID = 365353683
bot = telebot.TeleBot(API_TOKEN)
TOTAL_TICKETS = 5
WEB_APP_URL = "https://gamme-430.github.io/DaimondLottery431/"

# --- FIREBASE FUNCTIONS ---
def get_sold_count():
    return db.reference('sales/count').get() or 0

def buy_ticket_db(user_id, username):
    ref_count = db.reference('sales/count')
    ref_buyers = db.reference('buyers')
    
    current_sold = ref_count.get() or 0
    if current_sold >= TOTAL_TICKETS:
        return False, current_sold

    ref_count.set(current_sold + 1)
    ref_buyers.push({'user_id': user_id, 'username': username})
    
    return True, current_sold + 1

def get_all_buyers():
    buyers_data = db.reference('buyers').get()
    if not buyers_data: return []
    return [(v['user_id'], v['username']) for v in buyers_data.values()]

def reset_db():
    db.reference('sales/count').set(0)
    db.reference('buyers').delete()

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 Start Game", web_app=WebAppInfo(url=WEB_APP_URL)))
    bot.send_message(message.chat.id, "👋 Bagat nagaan dhuftan!", reply_markup=markup)

@bot.message_handler(commands=['buy'])
def buy_ticket(message):
    success, current_sold = buy_ticket_db(message.from_user.id, message.from_user.username)
    if not success:
        bot.send_message(message.chat.id, "❌ Tikkeetiin dhumateera!")
        return
    bot.send_message(message.chat.id, f"✅ Tikkeetii bitattaniittu! ({current_sold}/{TOTAL_TICKETS})")

@bot.message_handler(commands=['draw'])
def admin_draw(message):
    if message.from_user.id != ADMIN_ID: return
    buyers = get_all_buyers()
    if not buyers:
        bot.send_message(message.chat.id, "❌ Namni hin jiru.")
        return
    winner = random.choice(buyers)
    bot.send_message(message.chat.id, f"🏆 Mo'ataan: @{winner[1]}")
    reset_db()

if __name__ == '__main__':
    bot.polling(none_stop=True)
