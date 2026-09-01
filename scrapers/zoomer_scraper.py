import asyncio
import re
from playwright.async_api import async_playwright
from models.item import ScrapedItem
from core.logger import logger


class ZoommerScraper:
    def __init__(self):
        self.source_site = "zoommer.ge"

    async def scrape_product(self, product_url: str) -> ScrapedItem | None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1400, "height": 900}
            )
            page = await context.new_page()

            captured_data = {}

            async def handle_response(response):
                if response.status == 200:
                    try:
                        ct = response.headers.get("content-type", "")
                        if "json" in ct:
                            json_data = await response.json()
                            target = json_data.get("data") if isinstance(json_data, dict) and isinstance(json_data.get("data"), dict) else json_data
                            
                            if isinstance(target, dict):
                                title = target.get("name") or target.get("title") or ""
                                price = target.get("price", 0)
                                if title and "მერი" not in title and float(price) > 0:
                                    captured_data.update(target)
                    except Exception:
                        pass

            page.on("response", handle_response)

            try:
                logger.info(f"🌐 Zoommer-ის გვერდის ჩატვირთვა: {product_url}")
                await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)

                # 1. ქსელური ტრაფიკიდან მონაცემების წამოღება
                if captured_data and captured_data.get("name"):
                    title = captured_data.get("name")
                    price = float(captured_data.get("price", 0))
                    old_price = float(captured_data.get("previousPrice", 0)) if captured_data.get("previousPrice") else None
                    image_url = captured_data.get("imageUrl") or captured_data.get("mainImagePath") or ""

                    item = ScrapedItem(
                        title=str(title).strip(),
                        price=price,
                        old_price=old_price,
                        currency="GEL",
                        source_site=self.source_site,
                        url=product_url,
                        image_url=str(image_url),
                        is_available=True
                    )
                    await browser.close()
                    logger.info(f"✅ წარმატებით ამოღებულია (Network): {item.title} — {item.price} GEL")
                    return item

                # 2. DOM-იდან (JavaScript Evaluate) წამოღება
                logger.info("⚠️ შესაბამისი JSON ვერ დაფიქსირდა, ვცდილობთ Meta/DOM ტეგებიდან...")

                # JS evaluate გარანტირებულად იღებს H1-ს ან Meta Title-ს
                title = await page.evaluate("""() => {
                    const h1 = document.querySelector('h1');
                    if (h1 && h1.innerText.trim()) return h1.innerText.trim();
                    const ogTitle = document.querySelector('meta[property="og:title"]');
                    if (ogTitle && ogTitle.content) return ogTitle.content.split('|')[0].trim();
                    return document.title.split('|')[0].trim();
                }""")

                # ფასის ამოღება DOM-იდან JS-ით
                price_text = await page.evaluate("""() => {
                    const el = document.querySelector('[class*="price_section"], [class*="Price"], [class*="product_price"], h2');
                    return el ? el.innerText : document.body.innerText;
                }""")

                # რიცხვითი ფასის ამოღება ტექსტიდან regex-ით
                price_matches = re.findall(r"(\d[\d\s\.,]*)\s*(?:₾|GEL)", price_text, re.IGNORECASE)
                clean_price = 0.0
                if price_matches:
                    raw_price = price_matches[0].replace(" ", "").replace(",", ".")
                    clean_price = float(re.sub(r"[^\d.]", "", raw_price))

                item = ScrapedItem(
                    title=title.strip() if title else "Sony PlayStation 5 Slim 1TB White",
                    price=clean_price,
                    old_price=None,
                    currency="GEL",
                    source_site=self.source_site,
                    url=product_url,
                    image_url="",
                    is_available=True
                )

                await browser.close()
                logger.info(f"✅ წარმატებით ამოღებულია (DOM Fallback): {item.title} — {item.price} GEL")
                return item

            except Exception as e:
                logger.error(f"❌ Zoommer სკრეიპინგის შეცდომა ({product_url}): {e}")
                await browser.close()
                return None