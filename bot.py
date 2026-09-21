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
# 2. Telegram Bot Logic
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
            
            # API 1
            url1 = f"https://api.zoneid.org/api/mlbb?id={user_id}&zone={zone_id}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            success = False
            username = None
            
            try:
                res1 = requests.get(url1, headers=headers, timeout=8)
                if res1.status_code == 200:
                    data1 = res1.json()
                    if isinstance(data1, dict):
                        username = data1.get("username") or data1.get("nickname") or data1.get("name")
                        if username:
                            success = True
            except:
                pass

            # API 2 (Backup)
            if not success:
                try:
                    url2 = f"https://order-api.codashop.com/initPayment.action"
                    # Backup API Call
                    url_alt = f"https://mobile-legends-api.vercel.app/api/mlbb?id={user_id}&zone={zone_id}"
                    res2 = requests.get(url_alt, headers=headers, timeout=8)
                    if res2.status_code == 200:
                        data2 = res2.json()
                        if isinstance(data2, dict):
                            username = data2.get("username") or data2.get("name")
                            if username:
                                success = True
                except:
                    pass

            if success and username:
                msg = f"===== MLBB ID Details =====\n\n"
                msg += f"ID : {user_id}\n"
                msg += f"Zone : {zone_id}\n"
                msg += f"Username : {username}\n"
                bot.reply_to(message, msg)
            else:
                bot.reply_to(message, "အချက်အလက် ရှာမတွေ့ပါ။ ID သို့မဟုတ် Zone ID မှားနေနိုင်ပါသည် သို့မဟုတ် API စာဗာ ငြိမ်နေပါသည်။")

        except Exception as e:
            bot.reply_to(message, "စနစ်ပိုင်းဆိုင်ရာ အမှားတစ်ခု ဖြစ်ပေါ်နေပါသည်။")
    else:
        bot.reply_to(message, "ကျေးဇူးပြု၍ `ID(ZoneID)` ပုံစံဖြင့် ရိုက်ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

# Bot Polling Run ခြင်း (Conflict error မတက်အောင် skip_pending=True ပါဝင်သည်)
bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
