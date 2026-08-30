from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List
from scrapers.base import BaseScrapper
from models.item import ScrapedItem
from config.settings import settings

class TechStoreScrapper(BaseScrapper):
    async def fetch_page(self) -> str:
        """გახსნის ბრაუზერს Playwright-ით და წამოიღებს სრულ HTML-ს"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.HEADLESS_MODE)
            page = await browser.new_page()

            # Anti-bot detection-ისთვის basic User-Agent
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            await page.goto(self.target_url, wait_until="domcontentloaded", timeout=60000)
            content = await page.content()
            await browser.close()
            return content
        async def parse(self, html_content: str) -> List[ScrapedItem]:
            """BeautifulSoup-ით მონაცემების ექსტრაქცია HTML-იდან"""
            soup = BeautifulSoup(html_content, "html.parser")
            items: List[ScrapedItem] = []

            # მაგალითისთვის: სელექტორები მოვარგოთ რეალურ სტრუქტურას
            # ეს ნაწილი დაკონკრეტდება იმ საიტის მიხედვით, რომელსაც ავირჩევთ
            for card in soup.select(".product-card, .item-card"):
                try:
                    title_elem = card.select_one(".product-title, .title")
                    price_elem = card.select_one(".price-current, .price")
                    url_elem = card.select_one("a[href]")

                    if title_elem and price_elem:
                        title = title_elem.get_text(strip=True)
                        # ტექსტიდან მხოლოდ ციფრების ექსტრაქცია
                        raw_price = price_elem.get_text(strip=True).replace(",", "")
                        price = float(''.join(c for c in raw_price if c.isdigit() or c == '.'))

                        link = url_elem['href'] if url_elem else self.target_url
                        if not link.startswith("http"):
                            link = f"{self.target_url.rstrip('/')}/{link.lstrip('/')}"

                        item = ScrapedItem(
                            title=title,
                            price=price,
                            currency="GEL",
                            source_site=self.site_name,
                            url=link,
                            is_available=True
                        )
                        items.append(item)
                except Exception:
                    continue
            return items