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
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            response = requests.get(url, headers=headers, timeout=12)
            
            if response.status_code == 200:
                try:
                    res_json = response.json()
                    
                    # API result စာသားဖွဲ့စည်းခြင်း
                    msg = f"===== MLBB ID Details =====\n\n"
                    msg += f"ID : {user_id}\n"
                    msg += f"Zone : {zone_id}\n"
                    
                    if isinstance(res_json, dict):
                        # data သို့မဟုတ် result key ပါမပါ စစ်ဆေးခြင်း
                        info = res_json.get("data", res_json)
                        if isinstance(info, dict):
                            for k, v in info.items():
                                msg += f"{k.capitalize()} : {v}\n"
                        else:
                            msg += f"Result : {info}\n"
                    else:
                        msg += f"Result : {res_json}\n"
                        
                    bot.reply_to(message, msg)
                except Exception:
                    # JSON မဟုတ်ဘဲ Text ပဲပြန်လာရင်လည်း တိုက်ရိုက်ပြပေးမည်
                    bot.reply_to(message, f"===== MLBB ID Details =====\n\n{response.text}")
            else:
                bot.reply_to(message, f"API စာဗာမှ တုံ့ပြန်မှု မရရှိပါ (Status Code: {response.status_code})။ ID နှင့် Zone ID မှန်မမှန် ပြန်စစ်ပါ။")
                
        except requests.exceptions.Timeout:
            bot.reply_to(message, "API စာဗာမှ တုံ့ပြန်ချိန် ကြာမြင့်နေပါသဖြင့် နောက်မှ ပြန်စမ်းပေးပါ။")
        except Exception as e:
            bot.reply_to(message, f"အမှားဖြစ်ပေါ်ခဲ့သည်: {str(e)}")
    else:
        bot.reply_to(message, "ကျေးဇူးပြု၍ `ID(ZoneID)` ပုံစံဖြင့် ရိုက်ပို့ပေးပါ။\nဥပမာ - `123456789(9876)`")

# Bot Polling Run ခြင်း
bot.infinity_polling(timeout=10, long_polling_timeout=5)
