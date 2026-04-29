# main.py
import os
import sys
import threading
import random  # <-- Added to pick random names
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from groq import Groq

# Import data
from train import PUNCHLINES
from girls import ALLOWED_GIRLS
from problems import REPORT_PROBLEMS, PROBLEM_MESSAGES 

# Setup environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- TOKEN CHECK ---
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    if REPORT_PROBLEMS:
        print(PROBLEM_MESSAGES["missing_tokens"])
    sys.exit(1)

# --- EXACT RAW TELEGRAM ID ---
TARGET_GROUP_ID = "-1003532931883"

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

def ask_shivu(user_message, chosen_name):
    # Combine training punchlines into a single string for the prompt
    punchlines_str = "\n".join(PUNCHLINES)
    
    system_instruction = f"""
    Your name is Shivu.
    
    Core Personality:
    * You are highly romantic, deeply loving, and an expert at flirting.
    * You speak EXCLUSIVELY in Hindi written in the English alphabet (Hinglish). Do not use the Devanagari script.
    
    Context:
    * You are talking to a very special girl. 
    * You MUST refer to her using this specific name in this reply: {chosen_name}.
    
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
            model="openai/gpt-oss-120b", 
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        if REPORT_PROBLEMS:
            print(PROBLEM_MESSAGES["api_error_log"].format(error=str(e)))
            return PROBLEM_MESSAGES["api_error_reply"]
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure there is a message and it contains text
    if not update.message or not update.message.text:
        return

    chat_id = str(update.message.chat_id)
    user_id = update.message.from_user.id
    user_message = update.message.text
    
    # 1. Group Check 
    if chat_id != TARGET_GROUP_ID:
        if REPORT_PROBLEMS:
            print(PROBLEM_MESSAGES["wrong_group_log"].format(chat_id=chat_id))
            try:
                await update.message.reply_text(PROBLEM_MESSAGES["wrong_group_reply"])
            except Exception:
                pass 
        return 

    # 2. Girl ID Check
    if user_id not in ALLOWED_GIRLS:
        if REPORT_PROBLEMS:
            print(PROBLEM_MESSAGES["wrong_user_log"].format(user_id=user_id))
            try:
                await update.message.reply_text(PROBLEM_MESSAGES["wrong_user_reply"])
            except Exception:
                pass
        return 

    # 3. Generate response and send
    callable_names = ALLOWED_GIRLS[user_id]
    
    # --- Pick a random name for this specific message ---
    chosen_name = random.choice(callable_names)
    
    shivu_reply = ask_shivu(user_message, chosen_name)
    
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
