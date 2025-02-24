from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext  # Note the lowercase 'filters'
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, unquote
import nest_asyncio
import re



# Get bot token from Railway environment variable
# TOKEN = os.getenv("TOKEN")
TOKEN = "7880635792:AAFjP0_DBgJujJq_6uWMomhCCCajMEoOvtU"

# Define the base URL
BASE_URL = "https://app.adjust.com/10h33jqp?campaign=monopoly-kashkick-ios-us-multilevel-20241007&adgroup=1369&creative=&label=b-bytzuirmlspxlofzcc&idfa=&click_id={click_id}&gps_adid=&android_id=%7Bandroid_id%7D&ip_address=172.56.61.75&campaign_id=683&creative_id=%7Bfile_id%7D&affiliate_id=1369&publisher_id=1369&subpublisher_id=mw0lkx0lbfgi&install_callback=kashkick_install%26transaction_id%{transaction_id}&event_callback_js4kik=kashkick_event%26goal_id%3D5329%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_7v6ibj=kashkick_event%26goal_id%3D5330%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_na6ujc=kashkick_event%26goal_id%3D336%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_wylggm=kashkick_event%26goal_id%3D337%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_9uj0ba=kashkick_event%26goal_id%3D357%26amount%3D%7Brevenue_usd%7D%26transaction_id%{transaction_id}&event_callback_1secun=kashkick_event%26goal_id%3D927%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_fyocg0=kashkick_event%26goal_id%3D928%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_q03m3p=kashkick_event%26goal_id%3D929%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_5alsot=kashkick_event%26goal_id%3D930%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_19fdwx=kashkick_event%26goal_id%3D6389%26adv_id%3D549%26transaction_id%{transaction_id}&session_callback=https%3A%2F%2Fkashkick.go2cloud.org%2Faff_goal%3Fa%3Dlsr%26goal_id%3D1740%26transaction_id%{transaction_id}%26adv_sub%3Dsession_data%26adv_sub2%3Db-bytzuirmlspxlofzcc&event_callback_l9bicgp=kashkick_event%26goal_id%3D7346%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_hw3rju=kashkick_event%26goal_id%3D7347%26adv_id%3D549%26transaction_id%{transaction_id}&event_callback_9uwta9=kashkick_event%26goal_id%3D6919%26adv_id%3D549%26transaction_id%{transaction_id}"


async def modify_url(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()

    # Manipulate URL using urljoin
    modified_url = extract_and_replace(user_input)

    await update.message.reply_text(f"Modified URL: {modified_url}")


def extract_and_replace(url: str) -> str:

    modified_url = BASE_URL[:]
      # Extract click_id (value between '=' and '&')
    click_id_match = re.search(r'click_id=([^&]+)', url)
    click_id = click_id_match.group(1) if click_id_match else None

    # Extract the first transaction_id (value after 'transaction_id%3D' and before '&')
    transaction_id_match = re.search(r'transaction_id%([^&]+)', url)
    transaction_id = transaction_id_match.group(1) if transaction_id_match else None

    if not click_id or not transaction_id:
        return "Invalid URL: Missing click_id or transaction_id."

    # Replace values in BASE_URL
    modified_url = modified_url.replace("{click_id}", click_id)
    modified_url = modified_url.replace("{transaction_id}", transaction_id)

    return modified_url

async def main() -> None:
    application = Application.builder().token(TOKEN).build()  # Create Application instance

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, modify_url))

    await application.run_polling(poll_interval=3, close_loop=False)

if __name__ == "__main__":
    nest_asyncio.apply()
    nest_asyncio.asyncio.run(main())

