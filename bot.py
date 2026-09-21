import telebot
import requests
import re

BOT_TOKEN = "8425441082:AAExkdFsmxL9hRKJP8yaq3J9I3FTe8p5p8M"
bot = telebot.TeleBot(BOT_TOKEN)

def check_mlbb_id(user_id, zone_id):
    url = f"https://api.vytal.id/mlbb?id={user_id}&zone={zone_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error: {e}")
    return None

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "👋 မင်္ဂလာပါ! MLBB ID စစ်ဆေးရန် ID နဲ့ Zone ID ကို ပို့ပေးပါဦး။\n\nဥပမာ - `123456789 (9876)`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def process_id(message):
    text = message.text.strip()
    match = re.search(r'(\d+)[^\d]+(\d+)', text)
    
    if not match:
        bot.reply_to(message, "❌ ပုံစံ မှားယွင်းနေပါသည်။ `123456789 (9876)` ပုံစံအတိုင်း ပို့ပေးပါ။")
        return

    user_id = match.group(1)
    zone_id = match.group(2)
    
    wait_msg = bot.reply_to(message, "🔎 ခဏစောင့်ပါ... ID စစ်ဆေးနေပါသည်။")

    data = check_mlbb_id(user_id, zone_id)

    if data and (data.get("status") == 200 or data.get("nickname")):
        nickname = data.get("nickname", "Unknown")
        region = data.get("region", "Myanmar")
        
        # MLBB API မှ တကယ့်အချက်အလက်များ
        d50 = "AVAILABLE ✅" if data.get("d50", True) else "NOT AVAILABLE ❌"
        d150 = "AVAILABLE ✅" if data.get("d150", True) else "NOT AVAILABLE ❌"
        d250 = "AVAILABLE ✅" if data.get("d250", True) else "NOT AVAILABLE ❌"
        d500 = "AVAILABLE ✅" if data.get("d500", True) else "NOT AVAILABLE ❌"
        
        wdp = "Available ✅" if data.get("wdp", True) else "NOT AVAILABLE ❌"
        web = "Available ✅" if data.get("web", False) else "NOT AVAILABLE ❌"
        meb = "Available ✅" if data.get("meb", False) else "NOT AVAILABLE ❌"

        reply_format = f"""
===== MLBB ID Details =====

UID    : {user_id} ({zone_id})
Name   : {nickname}
Region : {region}

xxxx Double Diamonds xxxx

50  + 50: {d50}
150 + 150: {d150}
250 + 250: {d250}
500 + 500: {d500}

xxxx Pass & Bundle xxxx

Weekly Diamond Pass : {wdp}
Weekly Elite Bundle : {web}
Monthly Epic Bundle : {meb}
"""
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass
        bot.reply_to(message, reply_format)
    else:
        try:
            bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass
        bot.reply_to(message, "❌ ID ရှာမတွေ့ပါ သို့မဟုတ် ID/Zone ID မှားယွင်းနေပါသည်။")

print("Bot is Running...")
bot.polling(none_stop=True)
