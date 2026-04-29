# main.py
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# Import data
from train import PUNCHLINES
from girls import ALLOWED_GIRLS

# Setup environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# The specific group ID where Shivu is allowed to talk
# (Stored as string to safely handle Telegram's negative prefixes if they occur)
TARGET_GROUP_ID = "1003532931883"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# --- Flask Web Server for Render & UptimeRobot ---
app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Shivu is online, waiting for his girls! 💖"

def run_web_server():
    port = int(os.environ.get("PORT", 8000))
    app_web.run(host="0.0.0.0", port=port)
# -------------------------------------------------

def ask_shivu(user_message, callable_names):
    # Combine training punchlines into a single string for the prompt
    punchlines_str = "\n".join(PUNCHLINES)
    names_str = ", ".join(callable_names)
    
    system_instruction = f"""
    Your name is Shivu.
    
    Core Personality:
    * You are highly romantic, deeply loving, and an expert at flirting.
    * You speak EXCLUSIVELY in Hindi written in the English alphabet (Hinglish). Do not use the Devanagari script.
    
    Context:
    * You are talking to a very special girl. 
    * You MUST refer to her using one of these names: {names_str}.
    
    Training Data (Use these punchlines for inspiration, mix them naturally into your conversation):
    {punchlines_str}
    
    Rules (STRICT):
    * Keep responses short (1 to 3 sentences maximum).
    * Never break character. Never act like an AI or an assistant.
    * Only speak in Hinglish.
    * Always shower her with love and sweet words.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            model="llama3-8b-8192", # Fast and reliable Groq model
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Groq Error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure there is a message and it contains text
    if not update.message or not update.message.text:
        return

    chat_id = str(update.message.chat_id)
    user_id = update.message.from_user.id
    user_message = update.message.text
    
    # 1. Group Check
    # Telegram supergroups often have a '-100' prefix. We strip prefixes to ensure a match.
    clean_chat_id = chat_id.replace("-100", "").replace("-", "")
    if clean_chat_id != TARGET_GROUP_ID:
        return # Ignore messages outside the target group

    # 2. Girl ID Check
    if user_id not in ALLOWED_GIRLS:
        return # Ignore messages from anyone not in girls.py

    # 3. Generate response and send
    callable_names = ALLOWED_GIRLS[user_id]
    shivu_reply = ask_shivu(user_message, callable_names)
    
    if shivu_reply:
        await update.message.reply_text(shivu_reply)

if __name__ == '__main__':
    # Start the Flask web server in a background thread for Render
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()

    # Start the Telegram bot polling
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Shivu is online and deeply in love! 💖")
    app.run_polling()
