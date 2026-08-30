import asyncio
from database.db import init_db, SessionLocal, ProductModel
from models.item import ScrapedItem
from services.telegram_bot import TelegramNotifier
from core.logger import logger

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
    
async def main():
    logger.info("🚀 MarketPulse Pipeline გაშვიებულია...")
    
    # 1. SQL ტაბულების ინიციალიზაცია MSSQL-ში
    init_db()

    # 2. ინსტანციების მომზადება
    notifier = TelegramNotifier()
    db = SessionLocal()

    try:
        # სატესტო მონაცემი (რომ შევამოწმოთ ბაზაც და Telegram-იც)
        test_item = ScrapedItem(
            title="Sony PlayStation 5 Digital Edition",
            price=1499.00,
            old_price=1799.00,
            currency="GEL",
            source_site="test_store",
            url="https://example.com/ps5-test-item",
            is_available=True
        )

        logger.info("📦 სატესტო მონაცემის დამუშავება...")
        await process_item(db, test_item, notifier)
        
        logger.info("✅ ტესტმა წარმატებით ჩაიარა!")

    except Exception as e:
        logger.error(f"❌ შეცდომა გაშვებისას: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())