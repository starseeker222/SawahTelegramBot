import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Get bot token from environment variable
TOKEN = os.getenv("TOKEN")

# Define the base URL
BASE_URL = "https://app.adjust.com/10h33jqp?campaign=monopoly-kashkick-ios-us-multilevel-20241007&adgroup=1369&creative=&label=b-bytzuirmlspxlofzcc&idfa=&click_id={click_id}&gps_adid=&android_id=%7Bandroid_id%7D&ip_address=172.56.61.75&campaign_id=683&creative_id=%7Bfile_id%7D&affiliate_id=1369&publisher_id=1369&subpublisher_id=mw0lkx0lbfgi&install_callback=kashkick_install%26transaction_id%{transaction_id}&event_callback_js4kik=kashkick_event%26goal_id%3D5329%26adv_id%3D549%26transaction_id%{transaction_id}"

# FastAPI app
app = FastAPI()

# Webhook URL - your deployed Vercel URL
WEBHOOK_URL = "https://sawah-telegram-bot.vercel.app/webhook"  # Ensure HTTPS

# Extract click_id and transaction_id from the input URL
def extract_and_replace(url: str) -> str:
    modified_url = BASE_URL[:]

    # Extract click_id
    click_id_match = re.search(r'click_id=([^&]+)', url)
    click_id = click_id_match.group(1) if click_id_match else None

    # Extract transaction_id
    transaction_id_match = re.search(r'transaction_id=([^&]+)', url)
    transaction_id = transaction_id_match.group(1) if transaction_id_match else None

    if not click_id or not transaction_id:
        return "Invalid URL: Missing click_id or transaction_id."

    # Replace placeholders
    modified_url = modified_url.replace("{click_id}", click_id)
    modified_url = modified_url.replace("{transaction_id}", transaction_id)

    return modified_url

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    user_input = update.get('message', {}).get('text', '').strip()

    # Process URL
    modified_url = extract_and_replace(user_input)

    # Send response
    return JSONResponse(content={"text": f"Modified URL: {modified_url}"})

# Set the Telegram webhook when Vercel starts the app
@app.on_event("startup")
async def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(await response.text())  # Debugging
