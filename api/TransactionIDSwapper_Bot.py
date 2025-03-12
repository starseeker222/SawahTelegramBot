import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Get bot token from environment variable
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is not set! Add it to your Vercel environment variables.")

# Define the base URL
BASE_URL_MONOPOLY = "https://app.adjust.com/10h33jqp?campaign=monopoly-kashkick-ios-us-multilevel-20241007&adgroup=1369&creative=&label=b-bytzuirmlspxlofzcc&idfa=&click_id={click_id}&gps_adid=&android_id=%7Bandroid_id%7D&ip_address=172.56.61.75&campaign_id=683&creative_id=%7Bfile_id%7D&affiliate_id=1369&publisher_id=1369&subpublisher_id=mw0lkx0lbfgi&install_callback=kashkick_install%26transaction_id%{transaction_id}&event_callback_js4kik=kashkick_event%26goal_id%3D5329%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_7v6ibj=kashkick_event%26goal_id%3D5330%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_na6ujc=kashkick_event%26goal_id%3D336%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_wylggm=kashkick_event%26goal_id%3D337%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_9uj0ba=kashkick_event%26goal_id%3D357%26amount%3D%7Brevenue_usd%7D%26transaction_id%{transaction_id}&event_callback_1secun=kashkick_event%26goal_id%3D927%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_fyocg0=kashkick_event%26goal_id%3D928%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_q03m3p=kashkick_event%26goal_id%3D929%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_5alsot=kashkick_event%26goal_id%3D930%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_19fdwx=kashkick_event%26goal_id%3D6389%26adv_id%3D549%26transaction_id%{transaction_id}&session_callback=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D1740%26transaction_id%{transaction_id}%26adv_sub%3Dsession_data%26adv_sub2%3Db-bytzuirmlspxlofzcc&event_callback_l9bicgp=kashkick_event%26goal_id%3D7346%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_hw3rju=kashkick_event%26goal_id%3D7347%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_9uwta9=kashkick_event%26goal_id%3D6919%26adv_id%3D549%26transaction_id%{transaction_id}"

BASE_URL_SCATTER = "https://app.adjust.com/1dwerd5a?campaign=[g%7CScatter][p%7Cios][id%7C17337]_us_incent_cpi&adgroup=b-9hanppbntx8xiseffj&creative=1462&idfa=&click_id={click_id}&gps_adid=&android_id=%7Bandroid_id%7D&ip_address=174.202.169.245&campaign_id=996&creative_id=%7Bfile_id%7D&affiliate_id=1462&publisher_id=1462&subpublisher_id=efi7me3km0in&tracker_limit=250000&cost_currency=USD&cost_type=CPI&cost_amount=15&install_callback=http%3A%2F%2Fkashkick.go2cloud.org%2Faff_lsr%3Ftransaction_id%{transaction_id}&event_callback_7vnxvp=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3565%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_jx6si9=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3562%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_ldwzzy=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3563%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_wqnypk=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3564%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_czs0l7=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D6273%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_ekt93n=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D6274%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_2dlynt=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D7642%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_y37v1t=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D7949%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_15h2j9=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D7950%26adv_id%3D619%26transaction_id%{transaction_id}"

# FastAPI app
app = FastAPI()

# Webhook URL - your deployed Vercel URL
WEBHOOK_URL = "https://sawah-telegram-bot.vercel.app/api/webhook"

# Extract click_id and transaction_id from the input URL
def extract_and_replace(url: str) -> str :

    #making replacing pipe characters with %7C
    url.replace('|', '%7C')

    searchRes = url.find('[g%7CScatter][p%7Cios][id%7C17337]_us_incent_cpi')

    base_url = ''
    modified_url = ''

    

    match searchRes:
        case -1 :
            base_url = BASE_URL_MONOPOLY [:]
            modified_url += 'Monopoly URL, '

        case _:
            base_url = BASE_URL_SCATTER[:]
            modified_url += 'Scatter URL, '
                
    modified_url += base_url[:]
    # Extract click_id
    click_id_match = re.search(r'click_id=([^&]+)', url)
    click_id = click_id_match.group(1) if click_id_match else None

    # Extract transaction_id
    transaction_id_match = re.search(r'transaction_id%([^&]+)', url)
    transaction_id = transaction_id_match.group(1) if transaction_id_match else None

    if not click_id or not transaction_id:
        return "Invalid URL: Missing click_id or transaction_id."

    # Replace placeholders
    modified_url = modified_url.replace("{click_id}", click_id)
    modified_url = modified_url.replace("{transaction_id}", transaction_id)

    return modified_url

async def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            print(f"Sent message response: {result}")  # Debugging

# Webhook endpoint
@app.post("/api/webhook")  # ✅ Fixed route
async def webhook(request: Request):
    update = await request.json()
    print("Received update:", update)  # Debugging

    # Extract chat_id and user message
    chat_id = update.get("message", {}).get("chat", {}).get("id")
    user_input = update.get("message", {}).get("text", "").strip()

    if not chat_id or not user_input:
        return JSONResponse(content={"error": "Invalid request format"}, status_code=400)
    
    # Process URL
    modified_url = extract_and_replace(user_input)

    # Send a reply to the user
    await send_telegram_message(chat_id, f"Modified URL: {modified_url}")

    return JSONResponse(content={"message": "Processed successfully"})

# Set the Telegram webhook when Vercel starts the app
@app.on_event("startup")
async def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(await response.text())  # Debugging
