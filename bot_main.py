from flask import Flask
from threading import Thread
import os
import telebot
from telebot import types
import tweepy
from supabase import create_client
from dotenv import load_dotenv

# 1. Load Keys
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Initialize Systems
bot = telebot.TeleBot(BOT_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
x_client = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

# 3. Global State for Editing
user_edit_state = {} 

print("🚀 BedTeaKE Command Center: ONLINE")

# --- HELPER: Send Approval Card ---
def send_approval_card(chat_id, post):
    markup = types.InlineKeyboardMarkup()
    btn_post = types.InlineKeyboardButton("✅ POST", callback_data=f"post_{post['id']}")
    btn_edit = types.InlineKeyboardButton("✏️ EDIT", callback_data=f"edit_{post['id']}")
    btn_trash = types.InlineKeyboardButton("🗑️ TRASH", callback_data=f"trash_{post['id']}")
    markup.row(btn_post, btn_edit, btn_trash)
    
    bot.send_message(chat_id, f"📝 **DRAFT:**\n\n`{post['content']}`", parse_mode="Markdown", reply_markup=markup)

# --- 1. COMMAND: /check (Review AI Drafts) ---
@bot.message_handler(commands=['check'])
def check_drafts(message):
    if str(message.chat.id) != ADMIN_ID: return

    # Fetch oldest DRAFT
    response = supabase.table("posts").select("*").eq("status", "DRAFT").limit(1).execute()
    
    if not response.data:
        bot.reply_to(message, "🤷‍♂️ Queue is empty. Text me to create a draft, or run 'content_engine.py'.")
        return

    send_approval_card(message.chat.id, response.data[0])

# --- 2. BUTTON HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    action, post_id = call.data.split("_")
    
    if action == "post":
        # Fetch content to ensure we have latest version
        data = supabase.table("posts").select("content").eq("id", post_id).execute()
        if data.data:
            tweet = data.data[0]['content']
            try:
                x_client.create_tweet(text=tweet)
                supabase.table("posts").update({"status": "PUBLISHED"}).eq("id", post_id).execute()
                bot.edit_message_text(f"✅ **PUBLISHED:**\n{tweet}", call.message.chat.id, call.message.message_id)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"⚠️ Error: {e}")
    
    elif action == "trash":
        supabase.table("posts").update({"status": "REJECTED"}).eq("id", post_id).execute()
        bot.edit_message_text("🗑️ **DELETED**", call.message.chat.id, call.message.message_id)
        
    elif action == "edit":
        user_edit_state[call.message.chat.id] = post_id
        bot.send_message(call.message.chat.id, "✍️ **EDIT MODE**\n\nReply with the new text below:")
        bot.answer_callback_query(call.id)

# --- 3. EDITING LISTENER (High Priority) ---
@bot.message_handler(func=lambda m: m.chat.id in user_edit_state)
def finish_editing(message):
    post_id = user_edit_state[message.chat.id]
    new_text = message.text
    
    # Update DB
    supabase.table("posts").update({"content": new_text}).eq("id", post_id).execute()
    
    # Clear State
    del user_edit_state[message.chat.id]
    
    bot.reply_to(message, "✅ Updated!")
    send_approval_card(message.chat.id, {"id": post_id, "content": new_text})

# --- 4. ADMIN MANUAL DRAFT (The Feature You Asked For) ---
@bot.message_handler(func=lambda m: str(m.chat.id) == ADMIN_ID and not m.text.startswith("/"))
def handle_admin_draft(message):
    tweet_text = message.text
    
    print(f"💾 Saving Admin Draft: {tweet_text}")
    data = {"content": tweet_text, "post_type": "MANUAL", "status": "DRAFT"}
    
    supabase.table("posts").insert(data).execute()
    
    # Get the ID of what we just inserted to show buttons
    latest = supabase.table("posts").select("*").order("id", desc=True).limit(1).execute()
    send_approval_card(message.chat.id, latest.data[0])

# --- 5. PUBLIC CONFESSIONS (Low Priority Catch-All) ---
@bot.message_handler(func=lambda m: True)
def handle_public(message):
    # If it reached here, it's not you, or it's not a command
    supabase.table("incoming_msgs").insert({
        "user_id": message.chat.id,
        "message_text": message.text
    }).execute()
    bot.reply_to(message, "🔥 Received. Stay tuned.")
    bot.send_message(ADMIN_ID, f"🔔 **New Confession!**\n{message.text}")
    # --- COMMAND: /start (The Welcome Auto-Reply) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🔥 **Welcome to BedTea KE uncut**\n\n"
        "You’re 100% anonymous here — no logs, no names.\n\n"
        "Drop your juiciest bedroom confession now → gets posted on @BedTeaKE "
        "tonight (zero details revealed).\n\n"
        "Or just say **'hi'** and I’ll guide you. ☕"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- FLASK SERVER (For Render "Keep Alive") ---
app = Flask('')

@app.route('/')
def home():
    return "BedTeaKE is Online! ☕"

def run_http():
    # Render expects the app to listen on port 8080 or the PORT env var
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

if __name__ == "__main__":
    keep_alive() # Starts the fake website
    bot.infinity_polling() # Starts the bot