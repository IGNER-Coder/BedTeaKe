# BedTeaKE ☕🇰🇪 | The Nairobi Confessions Engine

**BedTeaKE** is a full-stack automation agent that manages anonymous confessions and generates engaging debates for X (formerly Twitter). It uses a "Human-in-the-Loop" architecture, allowing an admin to curate, edit, and approve content via Telegram before it goes live.

## 🚀 Features

* **Anonymous Confessions:** Users send secrets via a Telegram Bot; the system anonymizes and stores them.
* **AI Content Generation:** Uses **Groq (Llama 3.3)** to generate controversial "Nairobi Dating" debates in mixed English/Sheng.
* **Admin Command Center:** A Telegram interface to Review, Edit, Trash, or Post drafts instantly.
* **Database Management:** **Supabase (PostgreSQL)** stores all incoming messages and outgoing drafts.
* **X API Integration:** automated posting via **Tweepy**.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **AI Model:** Groq Cloud (Llama-3.3-70b-versatile)
* **Database:** Supabase
* **Interface:** Telegram Bot API (`pyTelegramBotAPI`)
* **X Integration:** Tweepy (API v2)

## 📂 Project Structure

* `bot_main.py` - The core server. Listens to Telegram and handles the "Approve/Post" logic.
* `content_engine.py` - The AI generator. Brainstorms topics and saves them as drafts.
* `requirements.txt` - Dependencies list.

## ⚙️ Setup & Configuration

This project requires a `.env` file with the following credentials:

```ini
# X (Twitter) API
X_API_KEY=your_key
X_API_SECRET=your_secret
X_ACCESS_TOKEN=your_token
X_ACCESS_SECRET=your_token_secret

# AI & Database
GROQ_API_KEY=your_groq_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_CHAT_ID=your_telegram_id