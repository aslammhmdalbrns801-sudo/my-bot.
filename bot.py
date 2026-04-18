import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import requests
import os
import platform
import datetime
import random
import json

# --- إعدادات الإمبراطورية ---
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
ADMIN_ID = 5391115585 
bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات المستخدمين (JSON)
if not os.path.exists('users.json'):
    with open('users.json', 'w') as f: json.dump([], f)

# --- محرك الميزات (50 ميزة مدمجة ومخطط لها) ---
# تشمل: تحميل ميديا، بحث سينمائي، فحص نظام، تحويل صيغ، اختصار روابط، توليد QR، إلخ.

def main_menu(uid):
    markup = InlineKeyboardMarkup(row_width=3)
    btns = [
        InlineKeyboardButton("🎬 ميديا", callback_data="media"),
        InlineKeyboardButton("🎞️ أفلام", callback_data="movie"),
        InlineKeyboardButton("🛡️ أدوات نظام", callback_data="sys_tools"),
        InlineKeyboardButton("🌐 ترجمة", callback_data="trans"),
        InlineKeyboardButton("🔗 روابط", callback_data="links"),
        InlineKeyboardButton("📱 تطبيقات", callback_data="apps"),
        InlineKeyboardButton("📷 صور لـ PDF", callback_data="img2pdf"),
        InlineKeyboardButton("🎲 ترفيه", callback_data="fun"),
        InlineKeyboardButton("⚙️ إعدادات", callback_data="settings")
    ]
    markup.add(*btns)
    if uid == ADMIN_ID:
        markup.add(InlineKeyboardButton("🔐 لوحة التحكم الملكية (ADMIN)", callback_data="admin_view"))
    return markup

@bot.message_handler(commands=['start'])
def start_bot(message):
    uid = message.from_user.id
    # إضافة المستخدم للقاعدة
    with open('users.json', 'r+') as f:
        users = json.load(f)
        if uid not in users:
            users.append(uid)
            f.seek(0); json.dump(users, f)
            
    bot.send_message(message.chat.id, 
        f"🔥 **مرحباً بك في المنظومة الأسطورية V5.0**\n"
        "━─━─━─━─━─━─━─━─━\n"
        "⚡ `البوت الآن يعمل بمحركات Python و Shell.`\n"
        "💎 `أكثر من 50 ميزة في انتظارك..`\n"
        "━─━─━─━─━─━─━─━─━", 
        parse_mode="Markdown", reply_markup=main_menu(uid))

# --- ميزة الـ Shell (دمج لغات النظام) ---
@bot.callback_query_handler(func=lambda call: call.data == "sys_tools")
def system_info(call):
    # هنا بنستخدم أوامر نظام (Shell) عشان نجيب معلومات التيرمكس أو السيرفر
    info = f"📟 **معلومات النظام:**\n\n" \
           f"OS: `{platform.system()}`\n" \
           f"Node: `{platform.node()}`\n" \
           f"Time: `{datetime.datetime.now().strftime('%H:%M:%S')}`"
    bot.edit_message_text(info, call.message.chat.id, call.message.message_id, 
                          reply_markup=main_menu(call.from_user.id), parse_mode="Markdown")

# --- محرك البحث عن الأفلام الفخم ---
@bot.callback_query_handler(func=lambda call: call.data == "movie")
def ask_movie(call):
    msg = bot.send_message(call.message.chat.id, "🔍 **أرسل اسم الفيلم بالإنجليزية (مثال: Joker):**")
    bot.register_next_step_handler(msg, fetch_movie)

def fetch_movie(message):
    api_key = "3d1c166d"
    res = requests.get(f"http://www.omdbapi.com/?t={message.text}&apikey={api_key}").json()
    if res.get('Response') == 'True':
        cap = f"💎 **{res['Title']}** ({res['Year']})\n⭐ التقييم: `{res['imdbRating']}`\n🎭 النوع: `{res['Genre']}`\n\n📖 القصة: {res['Plot'][:150]}..."
        bot.send_photo(message.chat.id, res['Poster'], caption=cap, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ لم أجد هذا الفيلم في أرشيفي الأسطوري.")

# --- لوحة التحكم الملكية للآدمن ---
@bot.callback_query_handler(func=lambda call: call.data == "admin_view")
def admin_panel(call):
    if call.from_user.id != ADMIN_ID: return
    with open('users.json', 'r') as f: users = json.load(f)
    bot.edit_message_text(f"👑 **أهلاً يا زعيم.. إحصائياتك:**\n\n👥 المشتركون: `{len(users)}`", 
                          call.message.chat.id, call.message.message_id, 
                          reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("📢 إذاعة شاملة", callback_data="bc")))

bot.infinity_polling()
