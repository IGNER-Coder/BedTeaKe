import feedparser
import os
import random
from groq import Groq
from supabase import create_client
from dotenv import load_dotenv

# 1. Load Keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MODES ---
# 1. Reddit Mode (React to news)
# 2. Brainstorm Mode (Create pure content/debates)

BRAINSTORM_PROMPT = """
You are BedTeaKE, a creative Nairobi content creator. 
Generate 3 distinct, engaging, and slightly controversial tweet ideas about: 
- Modern Dating in Nairobi
- Money/Hustle culture
- Relationship drama (Sponsors, Kanairo situations)

Format the output as a Python list of strings.
Example: ["Tweet 1 text...", "Tweet 2 text...", "Tweet 3 text..."]
Keep them in the 'BedTeaKE' style: English + Sheng mix. Under 260 chars.
"""

def get_reddit_topic():
    print("📡 Scanning Reddit...")
    rss_url = "https://www.reddit.com/r/Kenya/top/.rss?t=day"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        return random.choice(feed.entries[:5]).title
    return None

def run_brainstorm():
    print("🧠 Brainstorming original ideas...")
    completion = groq_client.chat.completions.create(
        messages=[{"role": "system", "content": BRAINSTORM_PROMPT}],
        model="llama-3.3-70b-versatile",
    )
    # The AI will give us a block of text; we just want to save it as a draft to edit later
    raw_text = completion.choices[0].message.content
    
    # Clean up the text to get just the ideas (simple split)
    ideas = raw_text.split("\n")
    
    for idea in ideas:
        if len(idea) > 20: # Filter out short garbage lines
            print(f"💡 Saving Idea: {idea[:50]}...")
            supabase.table("posts").insert({
                "content": idea, 
                "post_type": "BRAINSTORM", 
                "status": "DRAFT"
            }).execute()

def run_reddit_mode():
    topic = get_reddit_topic()
    if not topic: return
    
    print(f"🗞️ Found Reddit Topic: {topic}")
    completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Write a spicy tweet (English+Sheng) about: " + topic},
        ],
        model="llama-3.3-70b-versatile",
    )
    tweet = completion.choices[0].message.content
    supabase.table("posts").insert({"content": tweet, "status": "DRAFT"}).execute()
    print("✅ Reddit Draft Saved.")

if __name__ == "__main__":
    # You can uncomment whichever one you want to run
    # run_reddit_mode() 
    run_brainstorm() # <--- Running this one to get fresh original ideas