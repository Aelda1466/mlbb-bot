import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


# ၁။ အပေါ်ဆုံးမှာ ဒီ Web Server Code ကို ကူးထည့်ပါ
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Bot is running!")


def run_web_server():
  port = int(os.environ.get("PORT", 8080))
  server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
  server.serve_forever()


threading.Thread(target=run_web_server, daemon=True).start()

# ----------------------------------------------------
# ၂။ ဒီအောက်မှာ သင့်ရဲ့ မူလ Bot Code များကို ဒီအတိုင်း ထားပေးပါ
# ----------------------------------------------------

import requests
import telebot

BOT_TOKEN = "8425441082:AAExkdFsmxL9hRKJP8yaq3J9I3FTe8p5p8M"
bot = telebot.TeleBot(BOT_TOKEN)

# ... (သင့်ရဲ့ ကျန်တဲ့ MLBB ID စစ်တဲ့ Code များ) ...

bot.infinity_polling()
