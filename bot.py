import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import glob

# التوكن الخاص بك
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
bot = telebot.TeleBot(TOKEN)

user_links = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً يا بطل! 🚀\nابعتلي أي لينك وهنزلهولك صوت أو فيديو فوراً.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        user_links[message.chat.id] = url
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("فيديو 🎬", callback_data="video"),
                   InlineKeyboardButton("صوت 🎵", callback_data="audio"))
        bot.reply_to(message, "اختار النوع:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    choice = call.data
    
    if not url:
        bot.send_message(chat_id, "الرابط ضاع، ابعته تاني.")
        return

    bot.edit_message_text("⏳ جاري التحميل والرفع... (لو الملف كبير والنت بطيء هياخد وقت)", chat_id=chat_id, message_id=call.message.message_id)
    
    try:
        # إعدادات متطورة لتخطي حماية يوتيوب وتحسين الرفع
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # خاصية لتخطي حظر يوتيوب للبوتات
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        if choice == "video":
            ydl_opts.update({
                'format': 'best[filesize<45M]/best', # تقليل الحجم شوية لضمان الرفع
                'outtmpl': f'{chat_id}_v.%(ext)s'
            })
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '128'}],
                'outtmpl': f'{chat_id}_a.%(ext)s'
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # البحث عن الملف
        files = glob.glob(f"{chat_id}_*")
        if files:
            file_path = files[0]
            with open(file_path, 'rb') as f:
                # رفع الملف مع مهلة زمنية 10 دقائق (600 ثانية)
                if choice == "video":
                    bot.send_video(chat_id, f, timeout=600)
                else:
                    bot.send_audio(chat_id, f, timeout=600)
            os.remove(file_path)
            bot.delete_message(chat_id, call.message.message_id)
        else:
            bot.send_message(chat_id, "فشل في إيجاد الملف، جرب لينك تاني.")

    except Exception as e:
        bot.send_message(chat_id, f"❌ حصل خطأ: {str(e)}")
        
    if chat_id in user_links: del user_links[chat_id]

print("البوت انطلق! 🚀")
bot.infinity_polling()

