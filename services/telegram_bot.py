import httpx
from config.settings import settings
from core.logger import logger
from models.item import ScrapedItem

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_price_alert(self, item: ScrapedItem, old_price: float) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram Bot Credentials არ არის მითითებული .env ფაილში")
            return False

        message = (
            f"🚨 **PRICE DROP ALERT!** 🚨\n\n"
            f"📌 **{item.title}**\n"
            f"💰 ძველი ფასი: ~{old_price}~ {item.currency}\n"
            f"🔥 ახალი ფასი: **{item.price}** {item.currency}\n"
            f"📉 ფასდაკლება: **{item.discount_percentage}%**\n"
            f"🌐 წყარო: {item.source_site.capitalize()}\n\n"
            f"🔗 [ნახე პროდუქტი]({item.url})"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode":"Markdown",
            "disable_web_page_preview":False
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    logger.info(f"Telegram alert გაიგზავნა: {item.title}")
                    return True
                else:
                    logger.error(f"Telegram API Error ({response.status_code}): {response.text}")
                    return False

            except Exception as e:
                logger.error(f"Telegram notification შეცდომა: {e}")
                return False