# CodeAlpha_WebScraping

**CodeAlpha Data Analytics Internship — Task 1: Web Scraping**

## Objective
Collect data from public web sources using Python, demonstrating HTML
structure handling, web navigation (pagination), and the creation of a
custom dataset tailored to a specific analysis need (public sentiment
around Electric Vehicle adoption).

## What's in this repo

| File | Purpose |
|---|---|
| `scripts/scrape_html_beautifulsoup.py` | Core deliverable: scrapes article-listing webpages using **BeautifulSoup**, parses HTML structure (titles, dates, authors, summaries, tags), and **automatically follows "next page" links** to demonstrate web navigation. |
| `scripts/scrape_twitter.py` | Secondary scraper for social media data, using the official X (Twitter) API v2 via **Tweepy**, with a `snscrape` fallback for no-API-key use. |
| `scripts/generate_dataset.py` | Generates a schema-identical sample dataset (1,200+ records) so the pipeline can be demonstrated end-to-end without live API credentials. |
| `data/sample_pages/` | Two local HTML pages (`ev_news_page1.html`, `ev_news_page2.html`) used to test the BeautifulSoup scraper's parsing and pagination logic. |
| `data/output/scraped_html_articles.csv` | Output of the BeautifulSoup scraper — 7 articles extracted across both pages. |
| `data/output/ev_adoption_tweets.csv` | Output of the dataset generator — 1,208 sample records. |

## How it works

### 1. BeautifulSoup HTML scraper (main deliverable)
```bash
pip install requests beautifulsoup4

# Test offline against the bundled sample pages
python scripts/scrape_html_beautifulsoup.py --local-dir data/sample_pages --start-page ev_news_page1.html

# Run against a real, live website (needs internet access)
python scripts/scrape_html_beautifulsoup.py --url https://your-target-site.com/news --max-pages 5
```
The script finds every `<div class="article-card">` element, extracts the
title/date/author/summary/tags from its children, then looks for an
`<a class="next-page">` link to move to the next page — repeating until
no further link is found. This is the same logic used for any real
multi-page listing site; only the CSS selectors need adjusting to match
the target site's markup.

### 2. Social media API scraper (secondary deliverable)
```bash
pip install tweepy
python scripts/scrape_twitter.py --backend tweepy --bearer-token YOUR_TOKEN --max-results 500
```
Requires a free Bearer Token from [developer.x.com](https://developer.x.com).

### 3. Sample dataset generator (supporting script)
```bash
pip install pandas numpy
python scripts/generate_dataset.py
```

## Data fields collected
**HTML scraper:** `article_id, title, date, author, summary, tags, source_page`
**Social scraper:** `tweet_id, date, time, username, verified, followers_count, text, hashtags, brand_mentioned, location, likes, retweets, replies, quotes, sentiment_label, language`

## Ethical & legal notes
- Checked target site structure before scraping; always review `robots.txt` and Terms of Service for any live target.
- Requests are throttled (`SLEEP_SECONDS`) to avoid overloading servers.
- Only publicly accessible data is collected — no login bypass or private data access.

## Internship
Submitted as part of the [CodeAlpha](https://www.codealpha.tech) Data Analytics Internship Program.
