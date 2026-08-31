import asyncio
from database.db import init_db, SessionLocal, ProductModel
from models.item import ScrapedItem
from services.telegram_bot import TelegramNotifier
from core.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.settings import settings

async def process_item(db_session, item: ScrapedItem, notifier: TelegramNotifier):
    """ამოწმებს ბაზაში პროდუქტს, ანახლებს ფასს და აგზავნის ალერტს საჭიროებისას"""
    existing_product = db_session.query(ProductModel).filter(ProductModel.url == item.url).first()

    if existing_product:
        # თუ ფასი შემცირდა, გავაგზავნოთ Telegram alert
        if item.price < existing_product.price:
            logger.info(f"🔥 ფასდაკლება დაფიქსირდა: {item.title} ({existing_product.price} -> {item.price})")
            await notifier.send_price_alert(item, old_price=existing_product.price)
            existing_product.old_price = existing_product.price
            existing_product.price = item.price
        else:
            logger.info(f"ℹ️ {item.title} — ფასი უცვლელია ({item.price} GEL)")
    else:
        # ახალი პროდუქტის ბაზაში დამატება
        logger.info(f"➕ ახალი პროდუქტის დამატება: {item.title}")
        new_product = ProductModel(
            title = item.title,
            price = item.price,
            old_price = item.old_price,
            currency = item.currency,
            source_site = item.source_site,
            url = item.url,
            image_url = item.image_url,
            is_available = item.is_available
        )
        db_session.add(new_product)
    db_session.commit()

async def run_pipeline():
    """სკრეიპინგის და ბაზაში განახლების ერთი ციკლი"""
    logger.info("🔄 იწყება სკრეიპინგის პერიოდული ციკლი...")
    db = SessionLocal()
    notifier = TelegramNotifier()

    try:
        test_item = ScrapedItem(
            title="Sony PlayStation 5 Digital Edition",
            price=1399.00,
            old_price=1799.00,
            currency="GEL",
            source_site="test_store",
            url="https://example.com/ps5-test-item",
            is_available=True
        )
        await process_item(db, test_item, notifier)
        logger.info("✅ ციკლი წარმატებით დასრულდა.")
    except Exception as e:
        logger.error(f"❌ შეცდომა ციკლის შესრულებისას: {e}")
    finally:
        db.close()

async def main():
    logger.info("🚀 MarketPulse Pipeline გაშვებულია...")
    init_db()

    await run_pipeline()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        'interval',
        minutes=settings.SCRAPE_INTERVAL_MINUTES
    )
    scheduler.start()
    logger.info(f"⏰ Scheduler აქტიურია! ციკლი გაიშვება ყოველ {settings.SCRAPE_INTERVAL_MINUTES} წუთში.")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 აპლიკაცია გაჩერდა.")
if __name__ == "__main__":
    asyncio.run(main())