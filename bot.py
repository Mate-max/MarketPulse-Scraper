import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config.settings import settings
from main import run_pipeline

# ლოგირების ჩართვა ტერმინალისთვის
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ამოწმებს ბოტის სტატუსს"""
    await update.message.reply_text("🟢 <b>MarketPulse სკრეიპერი აქტიურია!</b>", parse_mode="HTML")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ხელით გააშვებინებს ფასების გადამოწმებას"""
    await update.message.reply_text("🔍 <b>ფასების გადამოწმება დაიწყო...</b>", parse_mode="HTML")
    
    try:
        await run_pipeline()
        await update.message.reply_text("✅ <b>გადამოწმება წარმატებით დასრულდა!</b>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <b>შეცდომა გადამოწმებისას:</b> {e}", parse_mode="HTML")

if __name__ == "__main__":
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check))

    print("🤖 ბოტი გაეშვა...")
    app.run_polling()