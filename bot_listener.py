import os
import telebot
from supabase import create_client
from dotenv import load_dotenv

# 1. Load Keys
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Initialize Clients
bot = telebot.TeleBot(BOT_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("👂 BedTeaKE Listener is active... (Press Ctrl+C to stop)")

# --- COMMAND: /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to BedTeaKE!**\n\n"
        "I am the automated engine.\n"
        "Type any confession or secret below, and I will save it to the secure vault."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# --- COMMAND: /admin (Check Status) ---
@bot.message_handler(commands=['admin'])
def admin_status(message):
    # Simple check to see if bot knows it's you
    bot.reply_to(message, "🕵️ Admin System: Online & Listening.")

# --- LISTENER: Catch All Text Messages ---
@bot.message_handler(func=lambda message: True)
def handle_incoming_message(message):
    user_id = message.from_user.id
    text = message.text
    username = message.from_user.username or "Anonymous"

    print(f"📩 New Message from {username}: {text}")

    # 1. Save to Supabase
    try:
        data = {
            "user_id": user_id,
            "message_text": text,
            "is_processed": False
        }
        supabase.table("incoming_msgs").insert(data).execute()
        
        # 2. Reply to User
        bot.reply_to(message, "🔥 Received. Your secret is safe in the database.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        bot.reply_to(message, "⚠️ System Error: Could not save message.")

# 3. Keep the script running properly
bot.infinity_polling()