FROM python:3.12-slim

WORKDIR /app

# სისტემური დამოკიდებულებები matplotlib-ისთვის და MS SQL-ისთვის
RUN apt-get update && apt-get install -y \
    gcc g++ curl gnupg2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]