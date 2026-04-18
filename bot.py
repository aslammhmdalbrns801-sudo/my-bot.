import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import requests
import json

# --- إعدادات العظمة ---
TOKEN = '8750551644:AAGnsTxoKz7kOEDIOWhDWE-VQT2XRBWS82A'
ADMIN_ID = 5391115585  # هويتك كزعيم للبوت
bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات وهمية (يفضل استخدام SQLite لاحقاً)
db = {"users": set(), "maintenance": False}

# --- لوحات التحكم الفخمة ---

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎬 تحميل ميديا", callback_data="ui_download"),
        InlineKeyboardButton("🔍 بحث أفلام", callback_data="ui_movie"),
        InlineKeyboardButton("📱 تطبيقات", callback_data="ui_apps"),
        InlineKeyboardButton("🛡️ الدعم الفني", callback_data="ui_support")
    )
    return markup

def admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📢 إذاعة (Broadcast)", callback_data="adm_broadcast"),
        InlineKeyboardButton("📊 إحصائيات", callback_data="adm_stats"),
        InlineKeyboardButton("🛠️ وضع الصيانة", callback_data="adm_maint"),
        InlineKeyboardButton("🔙 العودة للقائمة", callback_data="ui_back")
    )
    return markup

# --- الأوامر الأساسية ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    db["users"].add(message.chat.id)
    name = message.from_user.first_name
    
    welcome_msg = (
        f"👑 **أهلاً بك يا {name} في المنظومة الأسطورية**\n"
        "━─━─━─━─━─━─━─━─━\n"
        "✨ `أنا مساعدك الذكي المتكامل..` \n"
        "⚡ `أستطيع التحميل، البحث، وتوفير الأدوات.`\n"
        "━─━─━─━─━─━─━─━─━\n"
        "👇 **اختر وجهتك من الأزرار أدناه:**"
    )
    
    # زر مخفي يظهر للآدمن فقط
    markup = main_menu()
    if message.from_user.id == ADMIN_ID:
        markup.add(InlineKeyboardButton("🔐 لوحة التحكم الملكية", callback_data="ui_admin"))
        
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

# --- معالجة الضغط على الأزرار ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    cid = call.message.chat.id

    if call.data == "ui_admin" and uid == ADMIN_ID:
        bot.edit_message_text("🎩 **مرحباً بك يا زعيم.. تحكم في إمبراطوريتك:**", cid, call.message.message_id, reply_markup=admin_panel(), parse_mode="Markdown")
    
    elif call.data == "ui_movie":
        msg = bot.send_message(cid, "🎬 **أرسل الآن اسم الفيلم الذي تبحث عنه بالإنجليزية:**")
        bot.register_next_step_handler(msg, search_movie)

    elif call.data == "adm_stats" and uid == ADMIN_ID:
        bot.answer_callback_query(call.id, "📊 جاري جلب البيانات..")
        bot.send_message(cid, f"📈 **إحصائيات القوة:**\n\n👥 المشتركون: `{len(db['users'])}` \n⚙️ الحالة: `نشط`", parse_mode="Markdown")

    elif call.data == "ui_back":
        start_cmd(call.message)

# --- محرك بحث الأفلام (العظمة التقنية) ---

def search_movie(message):
    movie_name = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    # استخدام API مجاني لجلب معلومات الأفلام (OMDB مثال)
    # ملاحظة: يفضل الحصول على API KEY خاص بك من omdbapi.com
    api_key = "3d1c166d" # مفتاح تجريبي
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
    
    try:
        data = requests.get(url).json()
        if data['Response'] == 'True':
            info = (
                f"🎬 **الفيلم:** `{data['Title']}`\n"
                f"📅 **السنة:** `{data['Year']}`\n"
                f"⭐ **التقييم:** `{data['imdbRating']}/10`\n"
                f"🎭 **النوع:** `{data['Genre']}`\n\n"
                f"📖 **القصة:** {data['Plot'][:200]}..."
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📥 رابط التحميل (Google)", url=f"https://www.google.com/search?q=download+movie+{movie_name}"))
            
            bot.send_photo(message.chat.id, data['Poster'], caption=info, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.reply_to(message, "❌ **للأسف لم أجد فيلماً بهذا الاسم.. تأكد من الكتابة الصحيحة.**")
    except:
        bot.reply_to(message, "⚠️ **حدث خطأ في الاتصال بقاعدة بيانات الأفلام.**")

# --- ميزة الإذاعة (Broadcast) للآدمن ---

@bot.callback_query_handler(func=lambda call: call.data == "adm_broadcast")
def start_broadcast(call):
    msg = bot.send_message(call.message.chat.id, "📢 **أرسل الرسالة التي تريد نشرها لجميع المستخدمين:**")
    bot.register_next_step_handler(msg, send_to_all)

def send_to_all(message):
    count = 0
    for user in db["users"]:
        try:
            bot.send_message(user, f"📢 **رسالة من الإدارة:**\n\n{message.text}")
            count += 1
        except: continue
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الرسالة إلى `{count}` مستخدم بنجاح!")

print("🚀 المنظومة الأسطورية قيد التشغيل..")
bot.infinity_polling()
