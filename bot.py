import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config.settings import settings
from main import run_pipeline
from database.db import SessionLocal, ProductModel
from scrapers.zoomer_scraper import ZoommerScraper
from core.notifier import TelegramNotifier
from main import process_item
from utils.chart import generate_price_chart
from database.db import PriceHistoryModel

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

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ამატებს ახალ პროდუქტს მონიტორინგისთვის: /add <URL>"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>გთხოვთ მიუთითოთ ბმული!</b>\nმაგალითად: <code>/add https://zoommer.ge/...</code>",
            parse_mode="HTML"
        )
        return

    raw_url = context.args[0].strip()

    if "zoommer.ge" not in raw_url.lower():
        await update.message.reply_text("❌ <b>არასწორი ბმული!</b> ამ ეტაპზე მხოლოდ Zoommer.ge-ს მხარდაჭერა გვაქვს.", parse_mode="HTML")
        return

    await update.message.reply_text("⏳ <b>პროდუქტის დამუშავება დაიწყო...</b>", parse_mode="HTML")

    db = SessionLocal()
    try:
        # შევამოწმოთ უკვე ხომ არ არის ბაზაში
        existing = db.query(ProductModel).filter(ProductModel.url == raw_url).first()
        if existing:
            await update.message.reply_text(
                f"ℹ️ <b>ეს პროდუქტი უკვე მონიტორინგის ქვეშაა:</b>\n{existing.title} ({existing.price} GEL)",
                parse_mode="HTML"
            )
            return

        # დავასკრეიპოთ ახალი პროდუქტი
        zoomer = ZoommerScraper()
        notifier = TelegramNotifier()
        scraped_item = await zoomer.scrape_product(raw_url)

        if scraped_item:
            await process_item(db, scraped_item, notifier)
            await update.message.reply_text(
                f"✅ <b>პროდუქტი წარმატებით დაემატა!</b>\n\n"
                f"📦 <b>{scraped_item.title}</b>\n"
                f"💰 <b>ფასი:</b> {scraped_item.price} GEL",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ <b>პროდუქტის ინფორმაციის წამოღება ვერ მოხერხდა.</b>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <b>შეცდომა დამატებისას:</b> {e}", parse_mode="HTML")
    finally:
        db.close()

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"გამოაქვს ყველა მონიტორინგზე მყოფი პროდუქტის სია"""
    db = SessionLocal()
    try:
        products = db.query(ProductModel).all()
        if not products:
            await update.message.reply_text("📭 <b>ბაზაში პროდუქტები არ არის.</b>", parse_mode="HTML")
            return

        msg = "📋 <b>მონიტორინგზე მყოფი პროდუქტები:</b>\n\n"
        for p in products:
            msg += f"<b>ID: {p.id}</b> | {p.title[:30]}...\n💰 <b>{p.price} GEL</b>\n🔗 <a href='{p.url}'>ლინკი</a>\n\n"

        msg += "💡 <i>წასაშლელად გამოიყენეთ: /delete &lt;ID&gt;</i>"
        await update.message.reply_text(msg, parse_mode = "HTML", disable_web_page_preview = True)
    except Exception as e:
        await update.message.reply_text(f"❌ <b>შეცდომა სიის წამოღებისას:</b> {e}", parse_mode="HTML")

    finally:
        db.close()

async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"შლის პროდუქტს ID-ის მიხედვით /delete<ID>"""
    if not context.args:
        await update.message.reply_text("⚠️ <b>გთხოვთ მიუთითოთ პროდუქტის ID!</b>\nმაგალითად: <code>/delete 1</code>", parse_mode="HTML")
        return

    try:
        prod_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ <b>ID უნდა იყოს ციფრი!</b>", parse_mode="HTML")
        return

    db = SessionLocal()
    try:
        product = db.query(ProductModel).filter(ProductModel.id == prod_id).first()
        if not product:
            await update.message.reply_text(f"❌ <b>პროდუქტი ID={prod_id} ვერ მოიძებნა.</b>", parse_mode="HTML")
            return

        title = product.title
        db.delete(product)
        db.commit()

        await update.message.reply_text(f"🗑️ <b>პროდუქტი წარმატებით წაიშალა:</b>\n{title}", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <b>შეცდომა წაშლისას:</b> {e}", parse_mode="HTML")
    finally:
        db.close()

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"გამოაქვს ფასების ისტორიის გრაფიკი: /chart <ID>"""
    if not context.args:
        await update.message.reply_text("⚠️ <b>გთხოვთ მიუთითოთ პროდუქტის ID!</b>\nმაგალითად: <code>/chart 1</code>", parse_mode="HTML")
        return

    try:
        prod_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ <b>ID უნდა იყოს ციფრი!</b>", parse_mode="HTML") 
        return

    db = SessionLocal()
    try:
        product = db.query(ProductModel).filter(ProductModel.id == prod_id).first()
        if not product:
            await update.message.reply_text(f"❌ <b>პროდუქტი ID={prod_id} ვერ მოიძებნა.</b>", parse_mode="HTML")
            return

        # იღებს ფასების ისტორიას (დალაგებულს თარიღის მიხედვით)
        # თუ PriceHistoryModel გაქვს:
        history = db.query(PriceHistoryModel).filter(PriceHistoryModel.product_id == prod_id).order_by(PriceHistoryModel.timestamp.asc()).all()

        if not history or len(history) < 2:
            await update.message.reply_text("ℹ️ <b>გრაფის ასაგებად საკმარისი ისტორია არ არსებობს (საჭიროა მინიმუმ 2 ჩანაწერი).</b>", parse_mode="HTML")
            return

        data = [(h.timestamp, h.price) for h in history]
        chart_file = generate_price_chart(product.title, data, output_filename=f"chart_{prod_id}.png")

        if chart_file and os.path.exists(chart_file):
            with open(chart_file, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=f"📊 <b>ფასების ცვლილების გრაფიკი:</b>\n{product.title}", parse_mode="HTML")
            os.remove(chart_file) # დროებითი ფაილის წაშლა
        else:
            await update.message.reply_text("❌ <b>გრაფიკის შექმნა ვერ მოხერხდა.</b>", parse_mode="HTML")

    except Exception as e:
        await update.message.reply_text(f"❌ <b>შეცდომა გრაფიკის შექმნისას:</b> {e}", parse_mode="HTML")
    finally:
        db.close()

if __name__ == "__main__":
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("add", add_product))
    app.add_handler(CommandHandler("list", list_products))
    app.add_handler(CommandHandler("delete", delete_product))
    app.add_handler(CommandHandler("chart", chart_command))

    print("🤖 ბოტი გაეშვა...")
    app.run_polling()