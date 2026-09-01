import asyncio
from re import sub
from playwright.async_api import async_playwright
from models.item import ScrapedItem
from core.logger import logger

class ZoomerScraper:
    def __init__(self):
        self.sourse_site = "zoomer.ge"
        self.base_url = "https//zoomer.ge"

    async def scrape_product(self, product_url: str) -> ScrapedItem | None:
        """Zoommer.ge-ს კონკრეტული პროდუქტის გვერდიდან მონაცემების ამოღება"""
        async with async_playwright() as p:
            # Chromium ბრაუზერის გაშვება Headless რეჟიმში
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                logger.info(f"🌐 Zoommer-ის გვერდის ჩატვირთვა: {product_url}")
                await page.goto(product_url, wait_until="domcontentloaded", timeout=30000)