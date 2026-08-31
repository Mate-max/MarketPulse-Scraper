import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from database.db import ProductModel
from core.logger import logger

class DataExporter:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_to_excel(self, db_session: Session) -> str:
        """SQL ბაზიდან ამოაქვს მონაცემები და ინახავს Excel ფაილად"""
        try:
            products = db_session.query(ProductModel).all()
            if not products:
                logger.warning("⚠️ ექსპორტისთვის მონაცემები ბაზაში არ მოიძებნა.")
                return ""

            data = [
                {
                    "ID": p.id,
                    "Title": p.title,
                    "Price (GEL)": p.price,
                    "Old Price (GEL)": p.old_price,
                    "Source": p.source_site,
                    "URL": p.url,
                    "Last Updated": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else ""
                }
                for p in products
            ]

            df = pd.DataFrame(data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.export_dir, f"products_report_{timestamp}.xlsx")

            # Excel-ში შენახვა
            df.to_excel(file_path, index=False, engine="openpyxl")
            logger.info(f"📊 მონაცემები წარმატებით ექსპორტირდა: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Excel ექსპორტის შეცდომა: {e}")
            return ""