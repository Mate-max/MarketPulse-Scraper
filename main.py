import asyncio
from database.db import init_db, SessionLocal, ProductModel, PriceHistoryModel
from models.item import ScrapedItem
from core.notifier import TelegramNotifier
from core.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.settings import settings
from services.exporter import DataExporter
from scrapers.zoomer_scraper import ZoommerScraper

# Telegram Bot Imports
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bot import start, status, add_product, list_products, delete_product, chart_command


async def process_item(db, scraped_item, notifier):
    """ამუშავებს დასკრეიპილ ნივთს: ინახავს ბაზაში და წერს ისტორიას"""
    product = db.query(ProductModel).filter(ProductModel.url == scraped_item.url).first()

    if not product:
        product = ProductModel(
            title=scraped_item.title,
            price=scraped_item.price,
            old_price=scraped_item.old_price,
            currency=scraped_item.currency,
            source_site=scraped_item.source_site,
            url=scraped_item.url,
            image_url=scraped_item.image_url,
            is_available=scraped_item.is_available
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        history = PriceHistoryModel(product_id=product.id, price=scraped_item.price)
        db.add(history)
        db.commit()

        logger.info(f"➕ დაემატა ახალი პროდუქტი: {product.title}")
    else:
        if product.price != scraped_item.price:
            logger.info(f"📉 ფასი შეიცვალა პროდუქტზე: {product.title} ({product.price} -> {scraped_item.price})")
            await notifier.notify_price_drop(product, scraped_item.price)
            
            product.old_price = product.price
            product.price = scraped_item.price
            
            history = PriceHistoryModel(product_id=product.id, price=scraped_item.price)
            db.add(history)
            
            db.commit()
        else:
            logger.info(f"ℹ️ ფასი უცვლელია: {product.title}")


async def run_pipeline():
    """სკრეიპინგის და ბაზაში განახლების ერთი ციკლი"""
    logger.info("🔄 იწყება სკრეიპინგის პერიოდული ციკლი...")
    db = SessionLocal()
    notifier = TelegramNotifier()
    zoomer = ZoommerScraper()

    try:
        products = db.query(ProductModel).all()

        if not products:
            logger.info("ℹ️ ბაზაში პროდუქტები არ არის.")
            return

        for prod in products:
            logger.info(f"🔍 მოწმდება: {prod.title or prod.url}")
            scraped_item = await zoomer.scrape_product(prod.url)

            if scraped_item:
                await process_item(db, scraped_item, notifier)

        exporter = DataExporter()
        exporter.export_to_excel(db)
        logger.info("✅ ციკლი წარმატებით დასრულდა.")
    except Exception as e:
        logger.error(f"❌ შეცდომა ციკლის შესრულებისას: {e}")
    finally:
        db.close()


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ხელით გააშვებინებს ფასების გადამოწმებას"""
    await update.message.reply_text("🔍 <b>ფასების გადამოწმება დაიწყო...</b>", parse_mode="HTML")
    try:
        await run_pipeline()
        await update.message.reply_text("✅ <b>გადამოწმება წარმატებით დასრულდა!</b>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <b>შეცდომა გადამოწმებისას:</b> {e}", parse_mode="HTML")


async def main():
    logger.info("🚀 MarketPulse Pipeline & Bot გაშვებულია...")
    init_db()

    # 1. Telegram ბოტის ინიციალიზაცია
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("add", add_product))
    app.add_handler(CommandHandler("list", list_products))
    app.add_handler(CommandHandler("delete", delete_product))
    app.add_handler(CommandHandler("chart", chart_command))

    # 2. APScheduler-ის გაშვება
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        'interval',
        minutes=settings.SCRAPE_INTERVAL_MINUTES
    )
    scheduler.start()
    logger.info(f"⏰ Scheduler აქტიურია! ციკლი გაიშვება ყოველ {settings.SCRAPE_INTERVAL_MINUTES} წუთში.")

    # 3. ბოტის გაშვება
    async with app:
        await app.start()
        await app.updater.start_polling()
        logger.info("🤖 Telegram ბოტი მზადაა შეტყობინებების მისაღებად!")
        
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 აპლიკაცია გაჩერდა.")
            await app.updater.stop()
            await app.stop()


if __name__ == "__main__":
    asyncio.run(main())