import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5391115585

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ابعتلي لينك فيديو وأنا هنزلهولك صوت أو فيديو")

# استقبال اللينكات
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("🎧 صوت", callback_data=f"audio|{url}"),
            InlineKeyboardButton("🎬 فيديو", callback_data=f"video|{url}")
        ]
    ]

    await update.message.reply_text(
        "اختار نوع التحميل:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# التعامل مع الاختيار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    mode = data[0]
    url = data[1]

    await query.message.reply_text("⏳ جاري التحميل...")

    try:
        if mode == "audio":
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True
            }
        else:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.%(ext)s',
                'quiet': True
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if mode == "audio":
            await query.message.reply_audio(audio=open(filename, 'rb'))
        else:
            await query.message.reply_video(video=open(filename, 'rb'))

        os.remove(filename)

    except Exception as e:
        await query.message.reply_text("❌ حصل خطأ أو الرابط غير مدعوم")

# لوحة الأدمن
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ مش مصرح لك")

    await update.message.reply_text("⚙️ لوحة التحكم:\n- البوت شغال\n- تقدر تضيف ميزات")

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
