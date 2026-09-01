import requests
from config.settings import settings
from core.logger import logger

class TelegramNotifier:
    def __init__(self):
        # settings.py-დან იღებს BOT_TOKEN და CHAT_ID
        self.bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        self.chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

    def send_price_drop_alert(self, product_title: str, old_price: float, new_price: float, url: str):
        """ფასდაკლების შეტყობინება"""
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️ Telegram-ის პარამეტრები (.env) არ არის სრულად მითითებული.")
            return

        message = (
            f"🔥 **ფასდაკლების განგაში!** 🔥\n\n"
            f"📦 **პროდუქტი:** {product_title}\n"
            f"📉 **ძველი ფასი:** ~{old_price} GEL~\n"
            f"✅ **ახალი ფასი:** {new_price} GEL\n\n"
            f"🔗 [ნახე პროდუქტი საიტზე]({url})"
        )

        self.send_message(message)

    def send_message(self, text: str):
        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("📩 Telegram შეტყობინება წარმატებით გაიგზავნა!")
            else:
                logger.error(f"❌ Telegram შეცდომა: {response.text}")
        except Exception as e:
            logger.error(f"❌ Telegram-თან კავშირის შეცდომა: {e}")