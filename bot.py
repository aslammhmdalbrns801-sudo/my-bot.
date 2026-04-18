import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import requests
import os
import subprocess
import json
import datetime

# --- إعدادات الإمبراطورية ---
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
ADMIN_ID = 5391115585 
bot = telebot.TeleBot(TOKEN)

# تخزين مؤقت للبيانات
user_states = {}

# --- قائمة الـ 50 ميزة (هيكلة الوحدات) ---
def get_main_menu(uid):
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("📥 تحميل ميديا", callback_data="m_down"),
        InlineKeyboardButton("🔍 بحث أفلام", callback_data="m_movie"),
        InlineKeyboardButton("📱 تطبيقات", callback_data="m_apps"),
        InlineKeyboardButton("🛡️ أدوات هكر أخلاقي", callback_data="m_tools"),
        InlineKeyboardButton("🌐 ترجمة فورية", callback_data="m_trans"),
        InlineKeyboardButton("⚙️ فحص السيرفر", callback_data="m_sys"),
        InlineKeyboardButton("🎬 يوتيوب بحث", callback_data="m_yt"),
        InlineKeyboardButton("📸 إنستقرام", callback_data="m_insta"),
        InlineKeyboardButton("🎵 تحويل صوت", callback_data="m_audio")
    )
    if uid == ADMIN_ID:
        markup.add(InlineKeyboardButton("🔐 لوحة التحكم الملكية", callback_data="m_admin"))
    return markup

# --- رسالة الترحيب الأسطورية ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        f"💎 **أهلاً بك في المنظومة الأسطورية V6.0**\n"
        "━─━─━─━─━─━─━─━─━\n"
        "⚡ `تم دمج محركات الذكاء الاصطناعي والتحليل.`\n"
        "🚀 `البوت جاهز للتحميل من +1000 موقع.`\n"
        "━─━─━─━─━─━─━─━─━\n"
        "👇 **اختر القسم الذي تريد استكشافه:**"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu(message.from_user.id))

# --- المحلل الذكي للروابط (Core Intelligence) ---
@bot.message_handler(func=lambda m: m.text.startswith("http"))
def link_analyzer(message):
    url = message.text
    chat_id = message.chat.id
    msg = bot.reply_to(message, "🔍 **جاري تحليل الرابط بذكاء...**")
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'ميديا غير معروفة')
            user_states[chat_id] = url
            
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("🎬 فيديو (MP4)", callback_data="dl_video"),
                InlineKeyboardButton("🎵 صوت (MP3)", callback_data="dl_audio")
            )
            bot.edit_message_text(f"✅ **تم التحليل بنجاح!**\n📌 **العنوان:** `{title}`\n\nإيه الخطة؟", 
                                  chat_id, msg.message_id, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"❌ **الرابط غير مدعوم أو تالف.**", chat_id, msg.message_id)

# --- معالج التحميل الفخم ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("dl_"))
def download_handler(call):
    chat_id = call.message.chat.id
    url = user_states.get(chat_id)
    type = "mp3" if "audio" in call.data else "mp4"
    
    bot.edit_message_text(f"🚀 **بدأت عملية السحب الأسطورية ({type})...**", chat_id, call.message.message_id)
    
    output = f"downloads/{chat_id}_{datetime.datetime.now().timestamp()}.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio/best' if type == "mp3" else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output,
        'noplaylist': True,
    }
    
    if type == "mp3":
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if type == "mp3": filename = filename.rsplit('.', 1)[0] + ".mp3"

        with open(filename, 'rb') as f:
            if type == "mp3": bot.send_audio(chat_id, f, caption="🎵 تم الاستخراج بنجاح!")
            else: bot.send_video(chat_id, f, caption="🎬 تم التحميل بنجاح!")
        os.remove(filename)
    except Exception as e:
        bot.send_message(chat_id, "❌ حدث خطأ أثناء التحميل.")

# --- لوحة تحكم الآدمن (Admin Dashboard) ---
@bot.callback_query_handler(func=lambda call: call.data == "m_admin")
def admin_panel(call):
    if call.from_user.id != ADMIN_ID: return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 إذاعة للمشتركين", callback_data="adm_bc"),
               InlineKeyboardButton("📊 حالة السيرفر", callback_data="m_sys"))
    bot.edit_message_text("🎩 **لوحة تحكم الزعيم:**", call.message.chat.id, call.message.message_id, reply_markup=markup)

bot.infinity_polling()
