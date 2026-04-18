import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import glob
import requests

# توكن البوت
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 **أهلاً بك في البوت الشامل V2.0**\n\n"
                          "يمكنني تحميل:\n"
                          "🎵 أغاني وفيديوهات (YouTube, TikTok, etc.)\n"
                          "📱 تطبيقات وألعاب (روابط APK مباشرة)\n"
                          "📦 ملفات مضغوطة وروابط مباشرة\n\n"
                          "أرسل الرابط الآن وابدأ التجربة!", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    chat_id = message.chat.id
    
    if not url.startswith("http"):
        bot.reply_to(message, "⚠️ يرجى إرسال رابط صحيح.")
        return

    # فحص لو الرابط تطبيق أو ملف مباشر
    file_extensions = ('.apk', '.zip', '.exe', '.rar', '.pdf', '.jpg', '.png')
    if any(ext in url.lower() for ext in file_extensions):
        download_direct_file(message, url)
    else:
        # لو رابط ميديا (يوتيوب وغيرها)
        user_data[chat_id] = url
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🎬 فيديو", callback_data="video"),
            InlineKeyboardButton("🎵 صوت", callback_data="audio")
        )
        bot.reply_to(message, "📥 **تم اكتشاف رابط ميديا، اختر الصيغة:**", reply_markup=markup, parse_mode="Markdown")

def download_direct_file(message, url):
    msg = bot.reply_to(message, "⏳ **جاري فحص وتحميل الملف المباشر...**")
    try:
        file_name = url.split("/")[-1].split("?")[0]
        r = requests.get(url, stream=True, timeout=120)
        
        # التأكد من الحجم (التليجرام بوت له حدود في الرفع المباشر)
        total_size = int(r.headers.get('content-length', 0))
        if total_size > 50 * 1024 * 1024: # 50 ميجا
             bot.edit_message_text("❌ الحجم كبير جداً (أكبر من 50 ميجا). البوتات العادية لا تدعم رفع ملفات ضخمة من روابط مباشرة.", message.chat.id, msg.message_id)
             return

        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        
        with open(file_name, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"✅ تم تحميل ملفك:\n`{file_name}`", parse_mode="Markdown")
        os.remove(file_name)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ في تحميل الملف: {str(e)[:50]}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    if not url: return

    bot.edit_message_text("🚀 **بدأ التحميل... سأرسله لك فوراً.**", chat_id, call.message.message_id, parse_mode="Markdown")
    
    try:
        ydl_opts = {
            'quiet': True, 'noplaylist': True, 'default_search': 'ytsearch',
            'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s'
        }

        if call.data == "video":
            ydl_opts.update({'format': 'best[filesize<45M]/best'})
        else:
            ydl_opts.update({'format': 'bestaudio/best'})

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            if call.data == "video":
                bot.send_video(chat_id, f, caption="🎬 تم التحميل بنجاح!")
            else:
                bot.send_audio(chat_id, f, caption="🎵 تم التحميل بنجاح!")
        
        os.remove(filename)
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ: {str(e)[:100]}")

bot.infinity_polling()
