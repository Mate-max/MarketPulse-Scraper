import asyncio
from database.db import init_db, SessionLocal, ProductModel, PriceHistoryModel, init_db
from models.item import ScrapedItem
from core.notifier import TelegramNotifier
from core.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.settings import settings
from services.exporter import DataExporter
from scrapers.zoomer_scraper import ZoommerScraper


async def process_item(db, scraped_item, notifier):
    """ამუშავებს დასკრეიპილ ნივთს: ინახავს ბაზაში და წერს ისტორიას"""
    product = db.query(ProductModel).filter(ProductModel.url == scraped_item.url).first()

    if not product:
        # ახალი პროდუქტის შექმნა
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
        
        # ისტორიაში პირველი ფასის ჩაწერა
        history = PriceHistoryModel(product_id=product.id, price=scraped_item.price)
        db.add(history)
        db.commit()

        logger.info(f"➕ დაემატა ახალი პროდუქტი: {product.title}")
    else:
        # თუ ფასი შეიცვალა
        if product.price != scraped_item.price:
            logger.info(f"📉 ფასი შეიცვალა პროდუქტზე: {product.title} ({product.price} -> {scraped_item.price})")
            
            # შეტყობინების გაგზავნა
            await notifier.notify_price_drop(product, scraped_item.price)
            
            # ფასის განახლება პროდუქტის ცხრილში
            product.old_price = product.price
            product.price = scraped_item.price
            
            # ახალი ფასის ჩაწერა ისტორიაში
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