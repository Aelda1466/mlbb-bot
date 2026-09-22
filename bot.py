import os
import re
import requests
import telebot

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_mlbb_name(user_id, zone_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    # API 1: Direct Working Endpoint
    try:
        url = f"https://api.mobilelegends.com/v1/player/info?id={user_id}&zone={zone_id}"
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            data = r.json()
            name = data.get("username") or data.get("data", {}).get("username")
            if name:
                return name
    except Exception:
        pass

    # API 2: Fallback API
    try:
        url2 = f"https://api.vhtg.xyz/api/game/mlbb?id={user_id}&zone={zone_id}"
        r2 = requests.get(url2, headers=headers, timeout=6)
        if r2.status_code == 200:
            data2 = r2.json()
            res = data2.get("data", {}) if isinstance(data2, dict) else {}
            name = res.get("username") or res.get("nickname") or data2.get("username")
            if name:
                return name
    except Exception:
        pass

    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "မင်္ဂလာပါ! MLBB ID စစ်ဆေးရန်အတွက်\n"
        "`ID(ZoneID)` ပုံစံဖြင့် ပို့ပေးပါ။\n\n"
        "ဥပမာ - `123456789(9971)`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_id_check(message):
    text = message.text.strip()
    
    match = re.match(r'^(\d+)\s*\(\s*(\d+)\s*\)$', text)
    if not match:
        bot.reply_to(message, "⚠️ ပုံစံ မှားယွင်းနေပါသည်။ `123456789(9971)` ပုံစံအတိုင်း ပို့ပေးပါ။", parse_mode='Markdown')
        return

    user_id = match.group(1)
    zone_id = match.group(2)

    wait_msg = bot.reply_to(message, f"⏳ `{user_id}({zone_id})` အချက်အလက် စစ်ဆေးနေပါသည်...", parse_mode='Markdown')

    player_name = get_mlbb_name(user_id, zone_id)

    if player_name:
        result_text = (
            f"===== MLBB ID Details =====\n\n"
            f"🆔 **UID**    : `{user_id} ({zone_id})`\n"
            f"👤 **Name**  : `{player_name}`\n\n"
            f"✅ **Account Status**: Verified"
        )
    else:
        result_text = f"❌ `{user_id}({zone_id})`\nအချက်အလက် ရှာမတွေ့ပါ။ ID သို့မဟုတ် Zone ID မှားယွင်းနေပါသည်။"

    bot.edit_message_text(result_text, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
