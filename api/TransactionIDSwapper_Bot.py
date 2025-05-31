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

BASE_URL_SCATTER = "https://app.adjust.com/1dwerd5a?campaign=[g%7CScatter][p%7Cios][id%7C17894]_us_incent_cpi_besitos&adgroup={ad_group}&label={label}&creative=mw0lkx0lbfgi&idfa=&click_id={click_id}&gps_adid=&android_id=%7Bandroid_id%7D&ip_address={ip_address}&campaign_id=996&creative_id=%7Bfile_id%7D&affiliate_id=Tier3&publisher_id=Tier3&subpublisher_id=mw0lkx0lbfgi&tracker_limit=250000&cost_currency=USD&cost_type=CPI&cost_amount=5&install_callback=http%3A%2F%2Fkashkick.go2cloud.org%2Faff_lsr%3Ftransaction_id%{transaction_id}&event_callback_jx6si9=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3565%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_ldwzzy=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3562%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_wqnypk=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3563%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_ekt93n=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D3564%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_15h2j9=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D6273%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_fkf5kx=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D6274%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_czs0l7=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D7642%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_2dlynt=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D7949%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_7vnxvp=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D7950%26adv_id%3D619%26transaction_id%{transaction_id}&label={label}"

BASE_URL_INFINITY = "https://app.adjust.com/1h70r5tm?campaign=[g%7CInfinity][p%7Cios][id%7C17895]_us_incent_cpi_besitos&adgroup={ad_group}&creative=mw0lkx0lbfgi&kashkick_click_id={kashkick_click_id}&partner_click_id={partner_click_id}&idfa=&click_id={click_id}&gps_adid=&android_id=%7Bandroid_id%7D&ip_address={ip_address}&campaign_id=1121&creative_id=Tier1&publisher_id=Tier1&subpublisher_id=mw0lkx0lbfgi&tracker_limit=250000&cost_currency=USD&cost_type=CPI&cost_amount=6&install_callback=kashkick_install%26transaction_id%{transaction_id}&event_callback_35ftlx=kashkick_event%26goal_id%3D5530%26amount%3D%7Brevenue_usd%7D%26transaction_id%{transaction_id}&event_callback_9unq65=kashkick_event%26goal_id%3D8461%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_wimzml=kashkick_event%26goal_id%3D5532%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_udoe1u=kashkick_event%26goal_id%3D8462%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_f4whh4=kashkick_event%26goal_id%3D5534%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_vio347=kashkick_event%26goal_id%3D5535%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_2jb9e1=kashkick_event%26goal_id%3D5536%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_bni811=kashkick_event%26goal_id%3D6960%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_33bthr=kashkick_event%26goal_id%3D6961%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_ewd85t=kashkick_event%26goal_id%3D6962%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_7n08et=kashkick_event%26goal_id%3D8459%26adv_id%3D619%26transaction_id%{transaction_id}&event_callback_o2jmnp=kashkick_event%26goal_id%3D8460%26adv_id%3D619%26transaction_id%{transaction_id}&label={label}"

BASER_URL_FRAKLE = "https://app.adjust.com/1kd24fr4?campaign=KK_Farkle_US_iOS_Besitos&adgroup=Tier2&creative=efi7me3km0in&idfa=&click_id={click_id}&gps_adid=&android_id={android_id}&ip_address=174.207.103.133&campaign_id=1192&creative_id=1514&publisher_id=1514&subpublisher_id=efi7me3km0in&tracker_limit=250000&cost_currency=USD&cost_type=CPI&cost_amount=4.5&install_callback=kashkick_install%26transaction_id%{transaction_id}&event_callback_tr536o=kashkick_event%26goal_id%3D6993%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_3rk1mg=kashkick_event%26goal_id%3D6994%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_ldfmlg=kashkick_event%26goal_id%3D6992%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_cr6ffy=kashkick_event%26goal_id%3D6991%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_idelug=kashkick_event%26goal_id%3D6987%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_q4i5nl=kashkick_event%26goal_id%3D6988%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_eibbsi=kashkick_event%26goal_id%3D9183%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_vvf1sk=kashkick_event%26goal_id%3D9184%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_ylbikw=kashkick_event%26goal_id%3D8234%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_pn0avk=kashkick_event%26goal_id%3D8313%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_qnegw6=kashkick_event%26goal_id%3D9181%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_s06459=kashkick_event%26goal_id%3D9182%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_j7bc5x=kashkick_event%26goal_id%3D9185%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_e5okmh=kashkick_event%26goal_id%3D9186%26adv_id%3D635%26transaction_id%{transaction_id}&event_callback_uwiue5=kashkick_event%26goal_id%3D9187%26adv_id%3D635%26transaction_id%{transaction_id}"

# FastAPI app
app = FastAPI()

# Webhook URL - your deployed Vercel URL
WEBHOOK_URL = "https://sawah-telegram-bot.vercel.app/api/webhook"

# Extract click_id and transaction_id from the input URL
def extract_and_replace(url: str) -> str :

    #making replacing pipe characters with %7C
    url = url.replace('|', '%7C')

    print (url)

    isScatter = any(substr in url for substr in ['[g%7CScatter][p%7Cios]'])

    base_url = ''
    modified_url = ''

    

    match isScatter:
        case False :

            # Is frakkle
            if any(substr in  url for substr in ['KK_Farkle_US_iOS']):
                base_url = BASER_URL_FRAKLE[:]
                modified_url += 'Frakkle URL, '
            
            # Is Infinity
            else:
                if any(substr in  url for substr in ['[g%7CInfinity][p%7Cios]']):
                    base_url = BASE_URL_INFINITY[:]
                    modified_url += 'Infinity URL, '
                
                else:
                    base_url = BASE_URL_MONOPOLY [:]
                    modified_url += 'Monopoly URL, '

        case True:
            base_url = BASE_URL_SCATTER[:]
            modified_url += 'Scatter URL, '
                
    modified_url += base_url[:]
    # Extract click_id
    click_id_match = re.search(r'click_id=([^&]+)', url)
    click_id = click_id_match.group(1) if click_id_match else None

    # region slots params
    ad_group_match = re.search(r'adgroup=([^&]+)', url)
    ad_gorup = ad_group_match.group(1) if ad_group_match else None

    label_match = re.search(r'label=([^&]+)', url)
    label = label_match.group(1) if label_match else None

    ip_address_match = re.search(r'ip_address=([^&]+)', url)
    ip_address = ip_address_match.group(1) if ip_address_match else None
    #endregion 

    #region infinity params
    kashkick_click_id_match = re.search(r'kashkick_click_id=([^&]+)', url)
    kashkick_click_id = kashkick_click_id_match.group(1) if kashkick_click_id_match else None

    partner_click_id_match = re.search(r'partner_click_id=([^&]+)', url)
    partner_click_id = partner_click_id_match.group(1) if partner_click_id_match else None
    #endregion



    app_id_match = re.search(r'id%7C([^]]+)', url)
    app_id = app_id_match.group(1) if app_id_match else None

    # Extract transaction_id
    transaction_id_match = re.search(r'transaction_id%([^&]+)', url)
    transaction_id = transaction_id_match.group(1) if transaction_id_match else None

    if not click_id or not transaction_id:
        return "Invalid URL: Missing click_id or transaction_id."
    

    # Replace placeholders
    if(app_id != None):
        modified_url = modified_url.replace("{app_id}", app_id)
    else:
        modified_url = modified_url.replace("{app_id}", '17337')
    
    #region slots params replace
    if(ad_gorup != None):
        modified_url = modified_url.replace("{ad_gorup}", ad_gorup)
    
    if(label != None):
        modified_url = modified_url.replace("{label}", label)
    
    if(ip_address != None):
        modified_url = modified_url.replace("{ip_address}", ip_address)
    #endregion

    #region infinity params replace
    if(kashkick_click_id != None):
        modified_url = modified_url.replace("{kashkick_click_id}", kashkick_click_id)
    
    if(partner_click_id != None):
        modified_url = modified_url.replace("{partner_click_id}", partner_click_id)
    #endregion

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
