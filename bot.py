from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔐 Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not found")

client = OpenAI(api_key=OPENAI_API_KEY)

# 💬 Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # STEP 1 — TRANSLATE
    translate_prompt = f"""
You are a native German copywriter.

Translate this English text into natural, engaging German for an advertising context.

Rules:
- Sound like a native speaker
- Keep it clear and appealing
- Avoid literal translation if it sounds unnatural
- Keep it concise, but prioritize naturalness

Text: {user_text}
"""

    translation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": translate_prompt}]
    ).choices[0].message.content.strip()

    # STEP 2 — REVIEW
    review_prompt = f"""
You are a native German copywriter and editor.

Review and improve the following German text.

Check for:
- naturalness (native-level)
- marketing appeal
- clarity and flow
- grammar

Fix it if needed, but:
- do NOT make it longer than necessary
- keep it concise and punchy
- do NOT add new ideas
- If the text is already good, keep it unchanged

Return only the final improved version.

Text: {translation}
"""

    final_text = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": review_prompt}]
    ).choices[0].message.content.strip()

    # 📤 Reply
    await update.message.reply_text(f"🇩🇪 {final_text}")


# 🚀 Run bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ Bot is running...")
app.run_polling()