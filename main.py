import os, base64, requests, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen-Image-Edit"

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is alive!"

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or "make it anime style"
    file = await update.message.photo[-1].get_file()
    img_data = requests.get(file.file_path).content
    await update.message.reply_text(f"⏳ جاي اعدلها: {caption}")
    b64 = base64.b64encode(img_data).decode()
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {"inputs": caption, "image": b64}
    try:
        r = requests.post(HF_URL, headers=headers, json=payload, timeout=180)
        if r.status_code != 200:
            await update.message.reply_text(f"فشل: {r.text[:500]}")
            return
        await update.message.reply_photo(photo=r.content, caption=f"✅ تم: {caption}")
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
