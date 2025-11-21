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

# --- PROMPT ENGINEERING (The New Vibe) ---

# 1. BRAINSTORM MODE (Pure Imagination)
BRAINSTORM_PROMPT = """
You are a controversial relationship columnist for a Nairobi blog.
Generate 3 distinct, engaging, and spicy tweet ideas.

TOPICS ALLOWED:
- Intimacy & Bedroom dynamics (18+ implied).
- Cheating & infidelity stories.
- Toxic exes and situationships.
- Gender wars (Men vs Women behavior).

TOPICS BANNED (Do NOT write about):
- Money, bills, rent, or hustle.
- Politics or taxes.

FORMATTING:
- Language: Strict English (The user will add slang later).
- Tone: Savage, direct, questioning, or storytelling.
- Length: Maximize the 280 limit. Make them detailed.
- Output: Python list of strings. Example: ["Idea 1", "Idea 2", "Idea 3"]
"""

# 2. REDDIT MODE (Reacting to News)
SYSTEM_PROMPT = """
You are a relationship commentator.
Take the provided Reddit topic and turn it into a spicy debate about relationships/intimacy.
Even if the topic is boring, twist it into a relationship angle.

- Language: English only.
- Tone: "Tea Master" / Gossip / Warning.
- Length: Around 240-260 characters.
- NO mention of money or finance.
"""

def get_reddit_topic():
    print("📡 Scanning Reddit...")
    rss_url = "https://www.reddit.com/r/Kenya/top/.rss?t=day"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        return random.choice(feed.entries[:5]).title
    return None

def run_brainstorm():
    print("🧠 Brainstorming spicy content...")
    completion = groq_client.chat.completions.create(
        messages=[{"role": "system", "content": BRAINSTORM_PROMPT}],
        model="llama-3.3-70b-versatile",
        temperature=0.9 # Higher creativity for wilder stories
    )
    
    raw_text = completion.choices[0].message.content
    
    # Clean up text
    ideas = raw_text.split("\n")
    count = 0
    
    for idea in ideas:
        # Clean formatting like "1. " or "- "
        clean_idea = idea.lstrip("1234567890.- ")
        
        if len(clean_idea) > 50: # Filter out garbage lines
            print(f"💡 Saving Idea: {clean_idea[:50]}...")
            supabase.table("posts").insert({
                "content": clean_idea, 
                "post_type": "BRAINSTORM", 
                "status": "DRAFT"
            }).execute()
            count += 1
            
    print(f"✅ Saved {count} new drafts.")

def run_reddit_mode():
    topic = get_reddit_topic()
    if not topic: return
    
    print(f"🗞️ Found Reddit Topic: {topic}")
    completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}"}
        ],
        model="llama-3.3-70b-versatile",
    )
    tweet = completion.choices[0].message.content
    supabase.table("posts").insert({"content": tweet, "status": "DRAFT"}).execute()
    print("✅ Reddit Draft Saved.")

if __name__ == "__main__":
    # Run the brainstorm mode to test the new "Spicy English" vibe
    run_brainstorm()