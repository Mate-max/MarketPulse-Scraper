# 🛒 MarketPulse — Zoommer Price Tracker Bot

MarketPulse არის ავტომატიზებული Python ბოტი და სკრეიპერი, რომელიც აკონტროლებს პროდუქტების ფასებს **Zoommer.ge**-ზე, ინახავს ისტორიას MS SQL Server-ში, აგენერირებს ფასების ცვლილების გრაფიკებს Matplotlib-ის გამოყენებით და შეტყობინებებს აგზავნის Telegram-ში.

---

## 🚀 ფუნქციონალი

* 🔗 **პროდუქტის დამატება:** Zoommer-ის ბმულის გაგზავნა და მონიტორინგზე აყვანა (`/add`).
* 📉 **ფასების მონიტორინგი:** ფასის ცვლილებისას ავტომატური შეტყობინება Telegram-ში.
* 📊 **გრაფიკების გენერაცია:** ფასების ისტორიის ვიზუალიზაცია Matplotlib-ით (`/chart`).
* 📋 **მართვა:** პროდუქტების სიის ნახვა (`/list`) და წაშლა (`/delete`).
* 📑 **Excel ექსპორტი:** მონაცემების ავტომატური შენახვა Excel ფაილში.

---

## 🛠️ ტექნოლოგიური სტეკი

* **Language:** Python 3.12
* **Framework:** `python-telegram-bot`
* **Database & ORM:** SQL Server (SQLEXPRESS), SQLAlchemy, `pyodbc`
* **Scraping & Data:** BeautifulSoup4, Requests, Pandas
* **Visualization:** Matplotlib
* **Scheduler:** APScheduler

---

## ვირტუალური გარემოს შექმნა და აქტივაცია
python -m venv venv
# Windows:
venv\Scripts\activate

## დამოკიდებულებების დაყენება
pip install -r requirements.txt

## .env ფაილის გამართვა შექმენით .env ფაილი და შეავსეთ:
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
DATABASE_URL=mssql+pyodbc://.\SQLEXPRESS/SmartInvoiceDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
SCRAPE_INTERVAL_MINUTES=60

## ბოტის გაშვება
python bot.py

## ბრძანება,აღწერა
/start,ბოტის გაშვება და ინსტრუქცია
/status,ბოტის სტატუსის შემოწმება
/add <URL>,Zoommer-ის პროდუქტის დამატება
/list,მონიტორინგზე მყოფი პროდუქტების სია
/chart <ID>,ფასების ცვლილების გრაფიკული ანალიზი
/delete <ID>,პროდუქტის წაშლა მონიტორინგიდან
/check,ფასების ხელით გადამოწმება
