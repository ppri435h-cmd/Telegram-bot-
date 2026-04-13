import os
import requests
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ENV VARIABLES (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Send me any prompt to generate image")

# GENERATE IMAGE
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text

    await update.message.reply_text("⏳ Generating image...")

    # Create prediction
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "version": "db21e45e7c6e9e4e1e7e3cdb9d6b6b1b7a4d5b8c9f0e7c6b5a4d3e2f1c0b9a8",
            "input": {
                "prompt": prompt
            }
        }
    )

    data = response.json()

    await update.message.reply_text("⚡ Processing...")

    # Poll result
    while True:
        result = requests.get(
            data["urls"]["get"],
            headers={
                "Authorization": f"Token {REPLICATE_API_TOKEN}"
            }
        ).json()

        if result["status"] == "succeeded":
            image_url = result["output"][0]
            await update.message.reply_photo(photo=image_url)
            break

        elif result["status"] == "failed":
            await update.message.reply_text("❌ Failed to generate")
            break

        time.sleep(2)

# APP START
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))

print("🔥 Bot Started")
app.run_polling()
