import os
import re
import requests
import telebot

# Environment Variable မှ BOT_TOKEN ကို ရယူခြင်း
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def get_mlbb_info(user_id, zone_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # API 1: ZoneID API
    try:
        url = f"https://api.zoneid.org/api/mlbb?id={user_id}&zone={zone_id}"
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            res = r.json()
            data = res.get("data", {}) if isinstance(res, dict) else {}
            name = data.get("username") or data.get("nickname") or data.get("name")
            if name:
                return name
    except Exception:
        pass

    # API 2: OrderKu API
    try:
        url2 = f"https://orderku.id/api/v1/game/mobile-legends/?id={user_id}&zone={zone_id}"
        r2 = requests.get(url2, headers=headers, timeout=5)
        if r2.status_code == 200:
            res2 = r2.json()
            name = res2.get("nickname") or res2.get("username") or res2.get("data", {}).get("username")
            if name:
                return name
    except Exception:
        pass

    # API 3: SmileOne / Alternative Payload API
    try:
        url3 = "https://smileone.com/api/v1/checkrole"
        payload = {"user_id": user_id, "zone_id": zone_id, "pid": 13}
        r3 = requests.post(url3, json=payload, headers=headers, timeout=5)
        if r3.status_code == 200:
            res3 = r3.json()
            name = res3.get("username") or res3.get("data", {}).get("username")
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
        "ဥပမာ - `123456789(9876)`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_id_check(message):
    text = message.text.strip()
    
    # ID နဲ့ ZoneID ပုံစံ စစ်ဆေးခြင်း 123456(1234)
    match = re.match(r'^(\d+)\s*\(\s*(\d+)\s*\)$', text)
    
    if not match:
        bot.reply_to(message, "⚠️ ပုံစံ မှားယွင်းနေပါသည်။ ကျေးဇူးပြု၍ `123456789(9876)` ပုံစံအတိုင်း ပို့ပေးပါ။", parse_mode='Markdown')
        return

    user_id = match.group(1)
    zone_id = match.group(2)

    wait_msg = bot.reply_to(message, f"⏳ `{user_id}({zone_id})`\nခဏစောင့်ပေးပါ။ အချက်အလက်များ စစ်ဆေးနေပါသည်...", parse_mode='Markdown')

    try:
        player_name = get_mlbb_info(user_id, zone_id)
        
        if player_name:
            result_text = (
                f"🎮 **MLBB Account Info**\n\n"
                f"👤 **Name:** `{player_name}`\n"
                f"🆔 **ID:** `{user_id}`\n"
                f"🌐 **Zone ID:** `{zone_id}`"
            )
        else:
            result_text = f"❌ `{user_id}({zone_id})`\nအချက်အလက် ရှာမတွေ့ပါ။ ID သို့မဟုတ် Zone ID မှားယွင်းနေသည် သို့မဟုတ် API စာမ ငြိမ်နေပါ။"

        bot.edit_message_text(result_text, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id, parse_mode='Markdown')

    except Exception as e:
        bot.edit_message_text("❌ စစ်ဆေးစဉ် အမှားအယွင်းတစ်ခု ဖြစ်ပေါ်ခဲ့ပါသည်။ ခဏကြာမှ ပြန်လည်စမ်းသပ်ပေးပါ။", chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
