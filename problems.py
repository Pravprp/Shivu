# problems.py

# --- TOGGLE ERROR REPORTING ---
# Set this to True to see errors and send error replies in Telegram.
# Set this to False to make the bot silently ignore unauthorized users/groups.
REPORT_PROBLEMS = True

# --- PROBLEM MESSAGES ---
PROBLEM_MESSAGES = {
    # System Errors (Logged to Render only)
    "missing_tokens": "❌ CRITICAL ERROR: TELEGRAM_TOKEN or GROQ_API_KEY is missing! Check Render Environment Variables.",
    "api_error_log": "❌ GROQ API ERROR: {error}",
    
    # Telegram Replies (Sent to chat AND logged to Render)
    "api_error_reply": "Yaar, mera dimag thoda hang ho gaya hai (API Error). Mujhe bas 2 minute do! 😵‍💫",
    
    "wrong_group_log": "⚠️ DETECTED: Message from an unauthorized group (ID: {chat_id}).",
    "wrong_group_reply": "Mera dil yahan nahi lagta... Main sirf apne special group mein baat karta hoon! 💖",
    
    "wrong_user_log": "⚠️ DETECTED: Message from an unknown user (ID: {user_id}).",
    "wrong_user_reply": "Sorry ji, main sirf apni special girls se hi baat karta hoon! 😎💔"
}
