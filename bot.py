import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
import telebot


# =========================================================
# 1. RENDER WEB SERVER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"MLBB ID Checker Bot is running!"
        )

    def log_message(self, format, *args):
        pass


def start_web_server():
    port = int(os.environ.get("PORT", "10000"))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(f"Web server started on port {port}")

    server.serve_forever()


threading.Thread(
    target=start_web_server,
    daemon=True
).start()


# =========================================================
# 2. TELEGRAM BOT TOKEN
# =========================================================

# =========================================================
# IMPORTANT:
# ဒီနေရာမှာ မင်းရဲ့ BotFather TOKEN ကို ထည့်ပါ
# =========================================================

BOT_TOKEN = "8425441082:AAFA0BOy5ln7jueAr2tUnCCGTRwlF_yJO-g"


if BOT_TOKEN == "8425441082:AAFA0BOy5ln7jueAr2tUnCCGTRwlF_yJO-g":
    raise ValueError(
        "Please put your Telegram BotFather token in BOT_TOKEN."
    )


bot = telebot.TeleBot(BOT_TOKEN)


# =========================================================
# 3. MLBB API
# =========================================================

API_URL = "https://www.bybanana.my/api/v1/nickname"


# =========================================================
# 4. START COMMAND
# =========================================================

@bot.message_handler(commands=["start"])
def start_command(message):

    welcome = (
        "မင်္ဂလာပါ 🍊💜\n\n"
        "🎮 MLBB ID Checker မှ ကြိုဆိုပါတယ်။\n\n"
        "MLBB ID စစ်ရန်\n"
        "`ID(ZoneID)` ပုံစံနဲ့ ပို့ပေးပါ။\n\n"
        "ဥပမာ 👇\n"
        "`421289713(9971)`"
    )

    bot.reply_to(
        message,
        welcome,
        parse_mode="Markdown"
    )


# =========================================================
# 5. HELP COMMAND
# =========================================================

@bot.message_handler(commands=["help"])
def help_command(message):

    bot.reply_to(
        message,
        "🎮 MLBB ID Checker Help\n\n"
        "ID(ZoneID) ပုံစံနဲ့ ပို့ပေးပါ။\n\n"
        "ဥပမာ - `421289713(9971)`",
        parse_mode="Markdown"
    )


# =========================================================
# 6. CHECK MLBB ID
# =========================================================

@bot.message_handler(func=lambda message: True)
def check_mlbb_id(message):

    text = (message.text or "").strip()

    # -----------------------------------------------------
    # Check format
    # -----------------------------------------------------

    if "(" not in text or not text.endswith(")"):

        bot.reply_to(
            message,
            "❌ ID ပုံစံမမှန်ပါဘူး။\n\n"
            "ဒီလိုပို့ပေးပါ 👇\n"
            "`421289713(9971)`",
            parse_mode="Markdown"
        )

        return


    try:

        # -------------------------------------------------
        # Split ID and Zone ID
        # -------------------------------------------------

        id_part, zone_part = text.split("(", 1)

        user_id = id_part.strip()
        zone_id = zone_part[:-1].strip()


        # -------------------------------------------------
        # Validate numbers
        # -------------------------------------------------

        if not user_id.isdigit():

            bot.reply_to(
                message,
                "❌ MLBB ID မှာ နံပါတ်ပဲ ပါရပါမယ်။"
            )

            return


        if not zone_id.isdigit():

            bot.reply_to(
                message,
                "❌ Zone ID မှာ နံပါတ်ပဲ ပါရပါမယ်။"
            )

            return


        # -------------------------------------------------
        # Loading message
        # -------------------------------------------------

        loading_message = bot.reply_to(
            message,
            "🔍 MLBB Account စစ်ဆေးနေပါတယ်...\n\n"
            f"🆔 ID : {user_id}\n"
            f"🌐 Zone : {zone_id}\n\n"
            "⏳ ခဏစောင့်ပေးပါ..."
        )


        # -------------------------------------------------
        # API Request
        # -------------------------------------------------

        payload = {
            "code": "mlbb",
            "id": user_id,
            "zone": zone_id
        }


        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }


        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=20
        )


        print(
            "API STATUS:",
            response.status_code
        )

        print(
            "API RESPONSE:",
            response.text
        )


        # -------------------------------------------------
        # HTTP Error
        # -------------------------------------------------

        if response.status_code != 200:

            bot.edit_message_text(
                "❌ MLBB API က response မမှန်ပါဘူး။\n\n"
                f"HTTP Status : {response.status_code}\n\n"
                "ခဏနေပြီး ပြန်စမ်းကြည့်ပါ။",
                message.chat.id,
                loading_message.message_id
            )

            return


        # -------------------------------------------------
        # JSON Response
        # -------------------------------------------------

        try:

            data = response.json()

        except ValueError:

            bot.edit_message_text(
                "❌ API က JSON response မပေးပါဘူး။\n\n"
                "ခဏနေပြီး ပြန်စမ်းကြည့်ပါ။",
                message.chat.id,
                loading_message.message_id
            )

            return


        print("PARSED DATA:", data)


        # =================================================
        # FIND NICKNAME
        # =================================================

        nickname = None


        # -------------------------------------------------
        # Case 1: response is a dictionary
        # -------------------------------------------------

        if isinstance(data, dict):

            # Direct fields
            nickname = (
                data.get("nickname")
                or data.get("username")
                or data.get("name")
            )


            # -------------------------------------------------
            # data.nickname
            # -------------------------------------------------

            if not nickname:

                inner_data = data.get("data")

                if isinstance(inner_data, dict):

                    nickname = (
                        inner_data.get("nickname")
                        or inner_data.get("username")
                        or inner_data.get("name")
                    )


            # -------------------------------------------------
            # result.nickname
            # -------------------------------------------------

            if not nickname:

                result = data.get("result")

                if isinstance(result, dict):

                    nickname = (
                        result.get("nickname")
                        or result.get("username")
                        or result.get("name")
                    )


            # -------------------------------------------------
            # data as string
            # -------------------------------------------------

            if not nickname:

                if isinstance(data.get("data"), str):

                    nickname = data.get("data")


        # -------------------------------------------------
        # Case 2: API directly returns a string
        # -------------------------------------------------

        elif isinstance(data, str):

            nickname = data


        # =================================================
        # RESULT
        # =================================================

        if nickname:

            result_message = (
                "╔════════════════════╗\n"
                "     🎮 MLBB ID CHECK\n"
                "╚════════════════════╝\n\n"
                f"🆔 ID : {user_id}\n"
                f"🌐 Zone : {zone_id}\n"
                f"👤 Username : {nickname}\n\n"
                "✅ Account Found!"
            )

        else:

            result_message = (
                "╔════════════════════╗\n"
                "     🎮 MLBB ID CHECK\n"
                "╚════════════════════╝\n\n"
                f"🆔 ID : {user_id}\n"
                f"🌐 Zone : {zone_id}\n\n"
                "❌ Account မတွေ့ပါဘူး။\n\n"
                "ID / Zone ID မှန်မမှန် ပြန်စစ်ပေးပါ။"
            )


        # -------------------------------------------------
        # Edit loading message
        # -------------------------------------------------

        bot.edit_message_text(
            result_message,
            message.chat.id,
            loading_message.message_id
        )


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except requests.exceptions.Timeout:

        bot.edit_message_text(
            "⏰ MLBB API response ပြန်တာကြာနေပါတယ်။\n\n"
            "ခဏနေပြီး ထပ်စမ်းကြည့်ပါ။",
            message.chat.id,
            loading_message.message_id
        )


    except requests.exceptions.ConnectionError:

        bot.edit_message_text(
            "🌐 MLBB API Server ကို ချိတ်ဆက်လို့မရပါဘူး။\n\n"
            "API server ဘက်က ပြဿနာဖြစ်နိုင်ပါတယ်။",
            message.chat.id,
            loading_message.message_id
        )


    except Exception as e:

        print("BOT ERROR:", repr(e))

        try:

            bot.edit_message_text(
                "⚠️ Error တစ်ခုဖြစ်သွားပါတယ်။\n\n"
                "ခဏနေပြီး ထပ်စမ်းကြည့်ပါ။",
                message.chat.id,
                loading_message.message_id
            )

        except Exception:

            bot.reply_to(
                message,
                "⚠️ Error တစ်ခုဖြစ်သွားပါတယ်။"
            )


# =========================================================
# 7. START BOT
# =========================================================

print("===================================")
print("🤖 MLBB ID Checker Bot Starting...")
print("===================================")


bot.remove_webhook()


bot.infinity_polling(
    timeout=30,
    long_polling_timeout=30,
    skip_pending=True
)
