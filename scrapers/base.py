from abc import ABC, abstractmethod
from typing import List
from models.item import ScrapedItem
from core.logger import logger

class BaseScrapper(ABC):
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.site_name = self.__class__.__name__.replace("Scrapper", "").lower()

    @abstractmethod
    async def fetch_page(self) -> str:
        """ტვირთავს გვერდის HTML კოდს (Playwright ან HTTPX-ით)"""
        pass

    @abstractmethod
    async def parse(self, html_content: str) -> List[ScrapedItem]:
        """პარსავს HTML-ს და აბრუნებს Pydantic ScrapedItem ობიექტების სიას"""
        pass

    async def run(self) -> List[ScrapedItem]:
        """სკრეიპინგის სრული ციკლის გაშვება"""
        logger.info(f"[{self.site_name}] სკრეიპინგი დაიწყო: {self.target_url}")
        try:
            html = await self.fetch_page()
            items = await self.parse(html)
            logger.info(f"[{self.site_name}] წარმატებით წამოღებულია {len(items)} ნივთი")
            return items
        except Exception as e:
            logger.error(f"[{self.site_name}] სკრეიპინგის შეცდომა: {e}")
            return []