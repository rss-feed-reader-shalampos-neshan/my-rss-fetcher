import feedparser
import requests
from newspaper import Article
import os
import json
import re
import time

# خواندن فیدها از فایل feeds.txt
with open('feeds.txt', 'r', encoding='utf-8') as f:
    feeds = [line.strip() for line in f if line.strip()]

# فایل حافظه برای لینک‌های قبلی
PROCESSED_FILE = 'processed_urls.json'
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed_urls = set(json.load(f))
else:
    processed_urls = set()

new_processed = set()
os.makedirs('articles', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for idx, feed_url in enumerate(feeds):
    print(f"در حال بررسی فید: {feed_url}")
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"خطا در فید {feed_url}: {e}")
        continue

    for entry in feed.entries:
        article_url = entry.link
        if article_url in processed_urls:
            continue

        print(f"مقاله جدید یافت شد: {article_url}")
        try:
            article = Article(article_url, language='en')
            article.download()
            article.parse()

            title = article.title or "بدون عنوان"
            authors = ', '.join(article.authors) if article.authors else 'ناشناس'
            publish_date = article.publish_date.strftime('%Y-%m-%d') if article.publish_date else 'نامشخص'
            text_content = article.text

            if not text_content:
                print(f"متنی پیدا نشد: {article_url}")
                continue

            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
            filename = f"articles/{idx}_{safe_title}.txt"

            with open(filename, 'w', encoding='utf-8') as fout:
                fout.write(f"عنوان: {title}\n")
                fout.write(f"منبع: {article_url}\n")
                fout.write(f"نویسنده: {authors}\n")
                fout.write(f"تاریخ انتشار: {publish_date}\n")
                fout.write("\n" + "="*50 + "\n\n")
                fout.write(text_content)

            print(f"ذخیره شد: {filename}")
            processed_urls.add(article_url)
            new_processed.add(article_url)
            time.sleep(2)

        except Exception as e:
            print(f"خطا در استخراج {article_url}: {e}")
            continue

if new_processed:
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_urls), f, indent=2)
    print(f"{len(new_processed)} مقاله جدید اضافه شد.")
else:
    print("هیچ مقالۀ جدیدی یافت نشد.")
