import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import telebot

# ----------------------------------------------------
# 1. Render Port Binding Web Server
# ----------------------------------------------------
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MLBB Bot is Online!")

def start_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_web_server, daemon=True).start()

# ----------------------------------------------------
# 2. Telegram Bot Token Configuration
# ----------------------------------------------------
# မိမိ၏ Telegram Bot Token ကို အောက်ပါ နေရာတွင် အစားထိုးပါ
BOT_TOKEN = "8425441082:AAGPLxycy_gztFYgh0X4BCSuWIwyLhkShB0" 
bot = telebot.TeleBot(BOT_TOKEN)

# ----------------------------------------------------
# 3. Multi-API MLBB Lookup Logic
# ----------------------------------------------------
def get_mlbb_info(user_id, zone_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    # API 1: ZoneID API (Nested Data Structure Support)
    try:
        url1 = f"https://api.zoneid.org/api/mlbb?id={user_id}&zone={zone_id}"
        r = requests.get(url1, headers=headers, timeout=6)
        if r.status_code == 200:
            res_json = r.json()
            # JSON format အသီးသီးကို စစ်ဆေးခြင်း
            if isinstance(res_json, dict):
                # တိုက်ရိုက် သို့မဟုတ် data object ထဲတွင် ရှိမရှိ စစ်ဆေးခြင်း
                data_obj = res_json.get("data") if isinstance(res_json.get("data"), dict) else res_json
                name = data_obj.get("username") or data_obj.get("nickname") or data_obj.get("name") or data_obj.get("userName")
                if name: return name
    except Exception:
        pass

    # API 2: Vercel API
    try:
        url2 = f"https://mobile-legends-api.vercel.app/api/mlbb?id={user_id}&zone={zone_id}"
        r = requests.get(url2, headers=headers, timeout=6)
        if r.status_code == 200:
            res_json = r.json()
            if isinstance(res_json, dict):
                data_obj = res_json.get("data") if isinstance(res_json.get("data"), dict) else res_json
                name = data_obj.get("username") or data_obj.get("nickname") or data_obj.get("name") or data_obj.get("userName")
                if name: return name
    except Exception:
        pass

    return None
            

# ----------------------------------------------------
# 4. Telegram Bot Message Handlers
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MLBB ID စစ်ဆေးရန်အတွက် `ID(ZoneID)` ပုံစံဖြင့် ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

@bot.message_handler(func=lambda message: True)
def check_id(message):
    text = message.text.strip()
    if "(" in text and text.endswith(")"):
        try:
            id_part, zone_part = text.split("(")
            u_id = id_part.strip()
            z_id = zone_part.replace(")", "").strip()
            
            bot.reply_to(message, "ခဏစောင့်ပေးပါ၊ အချက်အလက်များ စစ်ဆေးနေပါသည်...")
            
            player_name = get_mlbb_info(u_id, z_id)
            
            if player_name:
                res_text = f"===== MLBB ID Details =====\n\nID : {u_id}\nZone : {z_id}\nUsername : {player_name}"
                bot.reply_to(message, res_text)
            else:
                bot.reply_to(message, "အချက်အလက် ရှာမတွေ့ပါ။ ID သို့မဟုတ် Zone ID မှားယွင်းနေပါသည် သို့မဟုတ် API စာဗာ ငြိမ်နေပါသည်။")
        except Exception:
            bot.reply_to(message, "အချက်အလက် ရယူရာတွင် အမှားတစ်ခု ဖြစ်ပေါ်နေပါသည်။ ခဏနေမှ ပြန်စမ်းပေးပါ။")
    else:
        bot.reply_to(message, "ကျေးဇူးပြု၍ `ID(ZoneID)` ပုံစံဖြင့် ရိုက်ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

# ----------------------------------------------------
# 5. Start Bot Polling
# ----------------------------------------------------
if __name__ == "__main__":
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception:
        pass
        
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
# Webhook အဟောင်းကို ဖျက်ရန်
bot.remove_webhook()

# Bot ကို စတင် run ရန်
bot.infinity_polling(skip_pending=True)
