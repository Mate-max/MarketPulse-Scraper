from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ScrapedItem(BaseModel):
    title: str = Field(..., description="პროდუქტის ან განცხადების დასახელება")
    price: float = Field(..., description="მიმდინარე ფასი")
    old_price: Optional[float] = Field(default=None, description="ძველი ფასი")
    currency: str = Field(..., description="პროდუქტის ბმული")
    source_site: str = Field(..., description="წყარო (მაგ. zoommer, myhome)")
    url: str = Field(..., description="პროდუქტის ბმული")
    image_url: Optional[str] = Field(default=None, description="სურათის ბმული")
    is_available: bool = Field(default=True, description="მარაგშია თუ არა")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="სკრეიპინგის დრო")

    @property
    def discount_percentage(self) -> Optional[float]:
        """ანგარიშობს ფასდაკლების პროცენტს"""
        if self.old_price and self.old_price > self.price:
            return round(((self.old_price - self.price) / self.old_price) * 100, 2)
        return 0.0