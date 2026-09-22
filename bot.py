import os
import re
import requests
import telebot

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in Railway Variables.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Temporary nickname API.
# We will replace/extend this with SmileOne later.
NICKNAME_API = "https://www.bybanana.my/api/v1/nickname"


# =========================================================
# PRODUCT SETTINGS
# =========================================================
# These are PLACEHOLDERS for Step 2.
# Later SmileOne API will determine the real availability.

DOUBLE_DIAMONDS = [
    ("50 + 50", False),
    ("150 + 150", False),
    ("250 + 250", False),
    ("500 + 500", False),
]

PASS_BUNDLES = [
    ("Weekly Diamond Pass", False),
    ("Weekly Elite Bundle", False),
    ("Monthly Epic Bundle", False),
]


# =========================================================
# START COMMAND
# =========================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    text = (
        "💜 <b>MLBB ID Checker</b>\n\n"
        "MLBB UID + Zone ID စစ်ရန်\n"
        "<code>UID(ZoneID)</code> ပုံစံနဲ့ ပို့ပေးပါ။\n\n"
        "ဥပမာ:\n"
        "<code>954255581(12790)</code>"
    )

    bot.reply_to(message, text)


# =========================================================
# HELP COMMAND
# =========================================================

@bot.message_handler(commands=["help"])
def help_command(message):

    text = (
        "💜 <b>အသုံးပြုနည်း</b>\n\n"
        "MLBB ID စစ်ရန်:\n"
        "<code>UID(ZoneID)</code>\n\n"
        "ဥပမာ:\n"
        "<code>954255581(12790)</code>\n\n"
        "Bot က UID, Zone ID နဲ့ Account Name ကို စစ်ပေးပါမယ်။"
    )

    bot.reply_to(message, text)


# =========================================================
# PARSE UID + ZONE
# =========================================================

def parse_mlbb_id(text):

    text = text.strip()

    # Accept:
    # 954255581(12790)
    # 954255581 (12790)

    pattern = r"^(\d+)\s*\(\s*(\d+)\s*\)$"

    match = re.match(pattern, text)

    if not match:
        return None, None

    user_id = match.group(1)
    zone_id = match.group(2)

    return user_id, zone_id


# =========================================================
# CHECK NICKNAME
# =========================================================

def check_nickname(user_id, zone_id):

    payload = {
        "code": "mlbb",
        "id": user_id,
        "zone": zone_id
    }

    try:

        response = requests.post(
            NICKNAME_API,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15
        )

        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"

        try:
            data = response.json()
        except ValueError:
            return None, "Invalid JSON response"

        return data, None

    except requests.exceptions.Timeout:
        return None, "Request timeout"

    except requests.exceptions.ConnectionError:
        return None, "Connection error"

    except requests.exceptions.RequestException as e:
        return None, str(e)

    except Exception as e:
        return None, str(e)


# =========================================================
# EXTRACT NAME FROM API RESPONSE
# =========================================================

def extract_nickname(data):

    if not isinstance(data, dict):
        return None

    # Possible direct fields
    possible_names = [
        "nickname",
        "username",
        "name",
        "player_name",
        "playerName"
    ]

    for key in possible_names:

        value = data.get(key)

        if value:
            return str(value)

    # Possible nested "data"
    nested = data.get("data")

    if isinstance(nested, dict):

        for key in possible_names:

            value = nested.get(key)

            if value:
                return str(value)

    # Possible nested "result"
    result = data.get("result")

    if isinstance(result, dict):

        for key in possible_names:

            value = result.get(key)

            if value:
                return str(value)

    return None


# =========================================================
# EXTRACT REGION
# =========================================================

def extract_region(data):

    if not isinstance(data, dict):
        return None

    possible_regions = [
        "region",
        "country",
        "country_name",
        "countryName"
    ]

    for key in possible_regions:

        value = data.get(key)

        if value:
            return str(value)

    nested = data.get("data")

    if isinstance(nested, dict):

        for key in possible_regions:

            value = nested.get(key)

            if value:
                return str(value)

    return None


# =========================================================
# FORMAT AVAILABILITY
# =========================================================

def availability_text(available):

    if available:
        return "AVAILABLE ✅"

    return "NOT AVAILABLE ❌"


def build_product_section():

    text = ""

    text += "xxxx Double Diamonds xxxx\n\n"

    for product_name, available in DOUBLE_DIAMONDS:

        text += (
            f"{product_name}: "
            f"{availability_text(available)}\n"
        )

    text += "\n"

    text += "xxxx Pass & Bundle xxxxx\n\n"

    for product_name, available in PASS_BUNDLES:

        text += (
            f"{product_name} : "
            f"{availability_text(available)}\n"
        )

    return text


# =========================================================
# BUILD FINAL RESULT
# =========================================================

def build_result(user_id, zone_id, nickname, region):

    if not nickname:
        nickname = "Unknown"

    if not region:
        region = "Unknown"

    text = (
        "===== MLBB ID Details =====\n\n"
        f"UID : {user_id} ({zone_id})\n"
        f"Name : {nickname}\n"
        f"Region : {region}\n\n"
        f"{build_product_section()}"
    )

    return text


# =========================================================
# HANDLE ALL NORMAL MESSAGES
# =========================================================

@bot.message_handler(func=lambda message: True)
def handle_message(message):

    text = message.text.strip()

    user_id, zone_id = parse_mlbb_id(text)

    # -----------------------------------------------------
    # Invalid format
    # -----------------------------------------------------

    if not user_id or not zone_id:

        bot.reply_to(
            message,
            "❌ Format မှားနေပါတယ်။\n\n"
            "ဒီလိုပုံစံနဲ့ ပို့ပေးပါ:\n"
            "<code>954255581(12790)</code>"
        )

        return

    # -----------------------------------------------------
    # Processing message
    # -----------------------------------------------------

    processing = bot.reply_to(
        message,
        "🔎 <b>MLBB Account စစ်ဆေးနေပါတယ်...</b>\n\n"
        "ခဏစောင့်ပေးပါ 💜"
    )

    # -----------------------------------------------------
    # API REQUEST
    # -----------------------------------------------------

    data, error = check_nickname(user_id, zone_id)

    # -----------------------------------------------------
    # API ERROR
    # -----------------------------------------------------

    if error:

        bot.edit_message_text(
            "❌ <b>Account စစ်ဆေးလို့မရပါ။</b>\n\n"
            f"Error: <code>{error}</code>\n\n"
            "ခဏနေပြီး ပြန်စမ်းကြည့်ပါ။",
            chat_id=processing.chat.id,
            message_id=processing.message_id
        )

        return

    # -----------------------------------------------------
    # GET NICKNAME
    # -----------------------------------------------------

    nickname = extract_nickname(data)

    region = extract_region(data)

    # -----------------------------------------------------
    # ACCOUNT NOT FOUND
    # -----------------------------------------------------

    if not nickname:

        bot.edit_message_text(
            "❌ <b>MLBB Account မတွေ့ပါ။</b>\n\n"
            f"UID : <code>{user_id}</code>\n"
            f"Zone : <code>{zone_id}</code>\n\n"
            "UID / Zone ID မှန်မမှန် ပြန်စစ်ပေးပါ။",
            chat_id=processing.chat.id,
            message_id=processing.message_id
        )

        return

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    result = build_result(
        user_id,
        zone_id,
        nickname,
        region
    )

    bot.edit_message_text(
        result,
        chat_id=processing.chat.id,
        message_id=processing.message_id
    )


# =========================================================
# START BOT
# =========================================================

print("===================================")
print("MLBB Telegram Bot is starting...")
print("===================================")

bot.remove_webhook()

bot.infinity_polling(
    timeout=30,
    long_polling_timeout=30,
    skip_pending=True
)
