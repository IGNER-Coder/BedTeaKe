import tweepy
import os
from dotenv import load_dotenv

# 1. Load your API Key and Secret (Consumer Keys)
load_dotenv()
API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")

if not API_KEY or not API_SECRET:
    print("❌ Error: Make sure X_API_KEY and X_API_SECRET are in your .env file.")
    exit()

# 2. Initialize the Auth Handler
# We use "oob" (Out of Band) which gives us a PIN code method
oauth1_user_handler = tweepy.OAuth1UserHandler(
    API_KEY, 
    API_SECRET, 
    callback="oob" 
)

# 3. Generate the Authorization URL
print("\n👇 CLICK THIS LINK TO AUTHORIZE YOUR BOT ACCOUNT 👇")
print(oauth1_user_handler.get_authorization_url(signin_with_twitter=True))
print("\n⚠️ INSTRUCTIONS:")
print("1. Copy the link above.")
print("2. Open a PRIVATE/INCOGNITO browser window.")
print("3. Log in to the Twitter account you want the bot to use (e.g., @BedTeaKE).")
print("4. Paste the link and click 'Authorize App'.")
print("5. Copy the PIN number displayed on the screen.")

# 4. Enter the PIN
verifier = input("\n🔢 Enter the PIN here: ")

# 5. Get the NEW Tokens
access_token, access_token_secret = oauth1_user_handler.get_access_token(verifier)

print("\n✅ SUCCESS! Here are your NEW keys for the bot account:")
print("-" * 50)
print(f"X_ACCESS_TOKEN={access_token}")
print(f"X_ACCESS_SECRET={access_token_secret}")
print("-" * 50)
print("👉 Copy these two lines and REPLACE the old ones in your .env file.")