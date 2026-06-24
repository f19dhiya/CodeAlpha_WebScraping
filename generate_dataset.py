"""
scrape_html_beautifulsoup.py
------------------------------
TASK 1: WEB SCRAPING (literal BeautifulSoup / HTML-parsing version)
Internship: CodeAlpha Data Analytics

This script satisfies the brief's exact wording: "Use Python libraries
like BeautifulSoup or Scrapy to extract data from websites... Learn to
handle HTML structure and web navigation to gather accurate data."

It scrapes an article-listing webpage (title, date, author, summary,
tags per article) and FOLLOWS THE "NEXT PAGE" LINK automatically -
demonstrating both HTML structure handling and web navigation.

TWO MODES
=========
1. --url <link>     : scrapes a LIVE public webpage over the internet.
                       Run this on your own laptop (needs internet access).
2. --local-dir <dir>: scrapes local HTML files instead of the live web.
                       Used here to prove the parsing logic works
                       correctly, since this sandboxed environment has
                       no general internet access. The HTML structure
                       (article-card / title / date / author / summary /
                       tags / next-page link) mirrors a typical real-world
                       news/blog listing page, so the exact same code
                       works unmodified on a live URL with that structure.

USAGE
=====
    # Test against the bundled sample pages (works anywhere, no internet)
    python scrape_html_beautifulsoup.py --local-dir data/sample_pages --start-page ev_news_page1.html

    # Real run against a live site (run on your own laptop)
    python scrape_html_beautifulsoup.py --url https://example-ev-news-site.com/news --max-pages 5

ETHICAL NOTE
============
Always check robots.txt and Terms of Service before scraping a real
site, throttle your requests (see SLEEP_SECONDS below), and only
collect data you're allowed to use.
"""

import argparse
import csv
import os
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SLEEP_SECONDS = 1.5  # politeness delay between page requests
HEADERS = {"User-Agent": "CodeAlphaInternshipBot/1.0 (educational project)"}

OUTPUT_PATH = "data/output/scraped_html_articles.csv"
FIELDNAMES = ["article_id", "title", "date", "author", "summary", "tags", "source_page"]


def parse_page(html, page_identifier):
    """
    Given raw HTML, extract one record per `.article-card` element.
    This is the core HTML-structure-handling logic: BeautifulSoup lets
    us navigate the DOM by tag name, class, and parent/child relationship
    instead of using brittle string/regex matching.
    """
    soup = BeautifulSoup(html, "html.parser")
    records = []

    for card in soup.find_all("div", class_="article-card"):
        title_tag = card.find("h2", class_="title")
        date_tag = card.find("span", class_="date")
        author_tag = card.find("span", class_="author")
        summary_tag = card.find("p", class_="summary")
        tag_elements = card.find_all("span", class_="tag")

        records.append({
            "article_id": card.get("data-id", ""),
            "title": title_tag.get_text(strip=True) if title_tag else "",
            "date": date_tag.get_text(strip=True) if date_tag else "",
            "author": author_tag.get_text(strip=True).replace("By ", "") if author_tag else "",
            "summary": summary_tag.get_text(strip=True) if summary_tag else "",
            "tags": ",".join(t.get_text(strip=True) for t in tag_elements),
            "source_page": page_identifier,
        })

    return records, soup


def find_next_page(soup, base_url_or_dir):
    """
    Web-navigation logic: look for a 'next page' link and resolve it to
    a full URL (live mode) or a local file path (local mode), or return
    None if we've reached the last page.
    """
    next_link = soup.find("a", class_="next-page")
    if not next_link or not next_link.get("href"):
        return None
    return urljoin(base_url_or_dir, next_link["href"])


def scrape_live(start_url, max_pages):
    """LIVE MODE: fetch real pages over HTTP. Run this on your laptop."""
    rows = []
    current_url = start_url
    page_count = 0

    while current_url and page_count < max_pages:
        print(f"Fetching: {current_url}")
        response = requests.get(current_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        page_records, soup = parse_page(response.text, current_url)
        rows.extend(page_records)
        print(f"  -> extracted {len(page_records)} articles")

        current_url = find_next_page(soup, current_url)
        page_count += 1
        time.sleep(SLEEP_SECONDS)

    return rows


def scrape_local(local_dir, start_page, max_pages):
    """
    LOCAL MODE: same parsing/navigation logic, applied to files on disk
    instead of live HTTP requests. Used here to validate the scraper
    without needing outbound internet access.
    """
    rows = []
    current_path = os.path.join(local_dir, start_page)
    page_count = 0

    while current_path and page_count < max_pages and os.path.exists(current_path):
        print(f"Reading: {current_path}")
        with open(current_path, "r", encoding="utf-8") as f:
            html = f.read()

        page_records, soup = parse_page(html, os.path.basename(current_path))
        rows.extend(page_records)
        print(f"  -> extracted {len(page_records)} articles")

        next_rel = find_next_page(soup, current_path)
        current_path = next_rel if next_rel and os.path.exists(next_rel) else None
        page_count += 1
        time.sleep(0.1)  # negligible delay for local files

    return rows


def write_csv(rows, path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows -> {path}")


def main():
    parser = argparse.ArgumentParser(description="BeautifulSoup HTML scraper with pagination")
    parser.add_argument("--url", help="Live start URL (requires internet access)")
    parser.add_argument("--local-dir", help="Directory of local HTML files to scrape instead")
    parser.add_argument("--start-page", default="ev_news_page1.html", help="Filename to start from in --local-dir mode")
    parser.add_argument("--max-pages", type=int, default=10)
    args = parser.parse_args()

    if args.url:
        rows = scrape_live(args.url, args.max_pages)
    elif args.local_dir:
        rows = scrape_local(args.local_dir, args.start_page, args.max_pages)
    else:
        raise SystemExit("Provide either --url (live) or --local-dir (offline test).")

    write_csv(rows)


if __name__ == "__main__":
    main()
