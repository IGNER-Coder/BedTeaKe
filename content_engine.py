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

# --- SAFETY CONFIGURATION (The Bouncer) ---
# If any of these words appear, the draft is auto-rejected.
BANNED_KEYWORDS = [
    "rape", "force", "assault", "non-consensual", "drunk", "asleep", 
    "minor", "child", "underage", "drug", "trafficking", "abuse", "violent"
]

def is_safe(text):
    text_lower = text.lower()
    for bad_word in BANNED_KEYWORDS:
        if bad_word in text_lower:
            print(f"⚠️ SAFETY ALERT: Blocked content containing '{bad_word}'")
            return False
    return True

# --- PROMPT ENGINEERING (The Intimate & Safe Vibe) ---
BRAINSTORM_PROMPT = """
You are a bold Relationship & Intimacy Coach for a Nairobi audience.
Generate 3 distinct, high-engagement tweet ideas. 

THEMES (Focus on Intimacy & Dynamics):
- Bedroom compatibility & preferences (Spicy but consensual).
- "Taboo" relationship questions (e.g., body count, age gaps).
- Gender debates (Men vs Women expectations).

FORMATS (Mix these up):
1. THE POLL: "Question? 👇 Like for [Option A] | RT for [Option B]"
2. THE DEBATE: "Unpopular Opinion: [Statement]. Argue in the comments."
3. THE STORY: A short scenario asking "Who is wrong here?"

STRICT SAFETY RULES:
- NO non-consensual content (rape, force, assault).
- NO mention of money, rent, or politics.
- Language: English only (User will add Sheng).
- Length: Maximize 260 chars.

Output: Python list of strings. Example: ["Poll text...", "Debate text...", "Story text..."]
"""

def run_brainstorm():
    print("🧠 Brainstorming intimate content...")
    try:
        completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": BRAINSTORM_PROMPT}],
            model="llama-3.3-70b-versatile",
            temperature=0.95 # High creativity
        )
        
        raw_text = completion.choices[0].message.content
        ideas = raw_text.split("\n")
        count = 0
        
        for idea in ideas:
            # Clean the text
            clean_idea = idea.lstrip("1234567890.- \"'").strip()
            
            # Filter 1: Length Check
            if len(clean_idea) < 20: 
                continue

            # Filter 2: Safety Check (The Bouncer)
            if is_safe(clean_idea):
                print(f"💡 Saving Safe Idea: {clean_idea[:40]}...")
                supabase.table("posts").insert({
                    "content": clean_idea, 
                    "post_type": "BRAINSTORM", 
                    "status": "DRAFT"
                }).execute()
                count += 1
            
        print(f"✅ Saved {count} safe drafts.")

    except Exception as e:
        print(f"❌ Error generating content: {e}")

if __name__ == "__main__":
    run_brainstorm()