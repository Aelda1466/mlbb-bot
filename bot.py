import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import telebot

# 1. Render Port အတွက် Web Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def start_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_web_server, daemon=True).start()

# 2. Telegram 8425441082:AAFA0BOy5ln7jueAr2tUnCCGTRwlF_yJO-g)
BOT_TOKEN = "8425441082:AAFA0BOy5ln7jueAr2tUnCCGTRwlF_yJO-g"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MLBB ID စစ်ဆေးရန်အတွက် `ID(ZoneID)` ပုံစံဖြင့် ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

@bot.message_handler(func=lambda message: True)
def check_mlbb_id(message):
    text = message.text.strip()
    
    if "(" in text and text.endswith(")"):
        try:
            id_part, zone_part = text.split("(")
            user_id = id_part.strip()
            zone_id = zone_part.replace(")", "").strip()
            
            bot.reply_to(message, "ခဏစောင့်ပေးပါ၊ အချက်အလက်များ စစ်ဆေးနေပါသည်...")
            
            url = f"https://api.zoneid.org/api/mlbb?id={user_id}&zone={zone_id}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, dict):
                    username = data.get("username") or data.get("nickname") or data.get("name") or "မသိပါ"
                    msg = f"===== MLBB ID Details =====\n\nID : {user_id}\nZone : {zone_id}\nUsername : {username}"
                    bot.reply_to(message, msg)
                else:
                    bot.reply_to(message, f"===== MLBB ID Details =====\n\n{data}")
            else:
                bot.reply_to(message, "အချက်အလက် ရှာမတွေ့ပါ။ ID သို့မဟုတ် Zone ID မှားယွင်းနေပါသည်။")
                
        except Exception:
            bot.reply_to(message, "အချက်အလက် ရယူရာတွင် အမှားတစ်ခု ဖြစ်ပေါ်နေပါသည်။")
    else:
        bot.reply_to(message, "ကျေးဇူးပြု၍ `ID(ZoneID)` ပုံစံဖြင့် ရိုက်ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

# 3. Webhook များကို ရှင်းထုတ်ပြီးမှ Polling စတင်ခြင်း (Conflict Error ကာကွယ်ရန်)
bot.remove_webhook()
bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
