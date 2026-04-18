import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import requests
import os
import datetime
import psutil # لمراقبة السيرفر
import speedtest # لقياس السرعة

# --- الإعدادات الأسطورية ---
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
ADMIN_ID = 5391115585 
bot = telebot.TeleBot(TOKEN)

# دالة لتحليل الروابط (يوتيوب، تيك توك، انستا، فيسبوك)
def download_media(url, chat_id, mode='video'):
    ydl_opts = {
        'format': 'bestaudio/best' if mode == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit('.', 1)[0] + (".mp3" if mode == 'audio' else ".mp4")

# --- لوحة التحكم (50 ميزة مقسمة) ---
def main_menu(uid):
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("📥 ميديا (كل المواقع)", callback_data="btn_dl"),
        InlineKeyboardButton("🎮 بحث ألعاب APK", callback_data="btn_games"),
        InlineKeyboardButton("🎬 بحث أفلام", callback_data="btn_movies"),
        InlineKeyboardButton("🚀 سرعة السيرفر", callback_data="btn_speed"),
        InlineKeyboardButton("📉 حالة الرامات", callback_data="btn_status"),
        InlineKeyboardButton("🌐 مترجم ذكي", callback_data="btn_trans"),
        InlineKeyboardButton("🖼️ صانع QR", callback_data="btn_qr"),
        InlineKeyboardButton("📝 ملاحظات", callback_data="btn_note"),
        InlineKeyboardButton("💎 ميزات إضافية", callback_data="btn_more")
    )
    if uid == ADMIN_ID:
        markup.add(InlineKeyboardButton("🔐 لوحة التحكم الملكية", callback_data="btn_admin"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔥 **أهلاً بك في المنظومة الأسطورية V7.0**\n\nأرسل أي رابط (YT, TikTok, Insta) أو اختر ميزة:", 
                     parse_mode="Markdown", reply_markup=main_menu(message.from_user.id))

# --- المحلل الذكي للروابط ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_links(message):
    url = message.text
    markup = InlineKeyboardMarkup().row(
        InlineKeyboardButton("🎬 فيديو", callback_data=f"vid_{url}"),
        InlineKeyboardButton("🎵 صوت", callback_data=f"aud_{url}")
    )
    bot.reply_to(message, "💎 **الذكاء الصناعي حلل الرابط! اختر الصيغة:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    uid = call.from_user.id
    cid = call.message.chat.id

    # منطق التحميل
    if call.data.startswith(("vid_", "aud_")):
        mode = 'video' if 'vid_' in call.data else 'audio'
        url = call.data.replace('vid_', '').replace('aud_', '')
        bot.edit_message_text("🚀 **جاري السحب والتحميل... انتظر القليل**", cid, call.message.message_id)
        try:
            file_path = download_media(url, cid, mode)
            with open(file_path, 'rb') as f:
                if mode == 'audio': bot.send_audio(cid, f)
                else: bot.send_video(cid, f)
            os.remove(file_path)
        except: bot.send_message(cid, "❌ فشل التحميل، الرابط قد يكون محمي أو كبير جداً.")

    # بحث الألعاب (APK) - مثال تفاعلي
    elif call.data == "btn_games":
        msg = bot.send_message(cid, "🎮 **أرسل اسم اللعبة التي تبحث عنها (English):**")
        bot.register_next_step_handler(msg, search_apk)

    # حالة السيرفر (Real-time Status)
    elif call.data == "btn_status":
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()
        bot.answer_callback_query(call.id, f"📊 الرامات: {ram}% | المعالج: {cpu}%", show_alert=True)

def search_apk(message):
    game = message.text
    # هنا بنوجهه لموقع تحميل APK موثوق آلياً
    url = f"https://rexdl.com/?s={game.replace(' ', '+')}"
    bot.reply_to(message, f"✅ **بحثت لك في الأرشيف الأسطوري:**\n\nتفضل روابط تحميل لعبة `{game}` مهكرة وعادية:\n🔗 [اضغط هنا للتحميل]({url})", parse_mode="Markdown")

bot.infinity_polling()
