from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import settings
from core.logger import logger
from datetime import datetime

Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "Products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    old_price = Column(Float, nullable=True)
    currency = Column(String(10), default="GEL")
    source_site = Column(String(100), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    image_url = Column(String(1000), nullable=True)
    is_available = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("SQL მონაცემთა ბაზა წარმატებით ინიციალიზდა")
    except Exception as e:
        logger.error(f"SQL მონაცემთა ბაზასთან კავშირის შეცდომა: {e}")