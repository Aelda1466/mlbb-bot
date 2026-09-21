import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import telebot

# ----------------------------------------------------
# 1. Render Port အတွက် Web Server
# ----------------------------------------------------
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

# ----------------------------------------------------
# 2. Telegram Bot Logic & MLBB API
# ----------------------------------------------------
BOT_TOKEN = "8425441082:AAExkdFsmxL9hRKJP8yaq3J9I3FTe8p5p8M"
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
            
            url = f"https://api.vytal.id/mlbb?id={user_id}&zone={zone_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # API မှ ပြန်လာသော အချက်အလက်များကို စာသားအဖြစ် ပြောင်းလဲခြင်း
                if isinstance(data, dict):
                    username = data.get("username", data.get("name", "မသိပါ"))
                    msg = f"===== MLBB ID Details =====\n\n"
                    msg += f"UID : {user_id} ({zone_id})\n"
                    msg += f"Name : {username}\n"
                    
                    # ကျန်ရှိသော အချက်အလက်များကို ထုတ်ပြခြင်း
                    for key, val in data.items():
                        if key not in ["username", "name", "id", "zone"]:
                            msg += f"{key} : {val}\n"
                else:
                    msg = f"===== MLBB ID Details =====\n\n{data}"
                
                bot.reply_to(message, msg)
            else:
                bot.reply_to(message, "အချက်အလက် ရှာမတွေ့ပါ။ ID နှင့် Zone ID မှန်မမှန် ပြန်စစ်ပါ။")
                
        except Exception as e:
            bot.reply_to(message, "အချက်အလက် ရယူရာတွင် အမှားတစ်ခု ဖြစ်ပေါ်နေပါသည်။ ID နှင့် Zone ID မှန်အောင် ရိုက်ပေးပါ။")
    else:
        bot.reply_to(message, "ကျေးဇူးပြု၍ `ID(ZoneID)` ပုံစံဖြင့် ရိုက်ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

# Bot Polling Run ခြင်း
bot.infinity_polling(timeout=10, long_polling_timeout=5)
