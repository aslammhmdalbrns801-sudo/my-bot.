import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import glob

# توكن البوت الخاص بك
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
bot = telebot.TeleBot(TOKEN)

# تخزين الروابط مؤقتاً
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ **أهلاً بك في بوت التحميل الذكي** ✨\n\n"
        "🚀 أنا جاهز لتحميل الفيديوهات والأغاني من أغلب المواقع.\n"
        "📎 فقط أرسل الرابط وسأقوم بالمهمة!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        user_data[message.chat.id] = url
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🎬 فيديو (Video)", callback_data="video"),
            InlineKeyboardButton("🎵 صوت (Audio)", callback_data="audio")
        )
        markup.add(InlineKeyboardButton("❌ إلغاء", callback_data="cancel"))
        bot.reply_to(message, "📥 **اختر الصيغة المطلوبة:**", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ من فضلك أرسل رابطاً صحيحاً (URL).")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    
    if call.data == "cancel":
        bot.edit_message_text("✅ تم الإلغاء.", chat_id, call.message.message_id)
        return

    if not url:
        bot.send_message(chat_id, "❌ انتهت الجلسة، أرسل الرابط مرة أخرى.")
        return

    bot.edit_message_text("⏳ **جاري المعالجة والتحميل...**\nقد يستغرق الأمر لحظات حسب حجم الملف.", chat_id, call.message.message_id, parse_mode="Markdown")
    
    try:
        # إعدادات التحميل الذكية
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'default_search': 'ytsearch', # البحث في حال كان الرابط محمي (مثل سبوتيفاي)
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        if call.data == "video":
            # اختيار أفضل جودة فيديو متاحة بحجم معقول للرفع
            ydl_opts.update({
                'format': 'best[filesize<48M]/best', 
                'outtmpl': f'downloads/{chat_id}_video.%(ext)s'
            })
        else:
            # تحميل الصوت بصيغته الأصلية لتجنب الحاجة لـ FFmpeg
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': f'downloads/{chat_id}_audio.%(ext)s'
            })

        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'ملف محمل')

        # البحث عن الملف الناتج
        files = glob.glob(f"downloads/{chat_id}_*")
        if files:
            file_path = files[0]
            with open(file_path, 'rb') as f:
                if call.data == "video":
                    bot.send_video(chat_id, f, caption=f"✅ **تم تحميل الفيديو:**\n{title}", parse_mode="Markdown", timeout=600)
                else:
                    bot.send_audio(chat_id, f, caption=f"✅ **تم تحميل الصوت:**\n{title}", parse_mode="Markdown", timeout=600)
            
            # تنظيف الملفات بعد الإرسال
            os.remove(file_path)
            bot.delete_message(chat_id, call.message.message_id)
        else:
            bot.send_message(chat_id, "❌ عذراً، فشل العثور على الملف بعد التحميل.")

    except Exception as e:
        error_msg = str(e)
        if "DRM" in error_msg:
            bot.send_message(chat_id, "❌ هذا المحتوى محمي بحقوق النشر (DRM) ولا يمكن تحميله مباشرة.")
        else:
            bot.send_message(chat_id, f"❌ حدث خطأ غير متوقع: {error_msg[:100]}...")
        
    if chat_id in user_data: del user_data[chat_id]

print("🚀 البوت يعمل الآن على السيرفر!")
bot.infinity_polling()
