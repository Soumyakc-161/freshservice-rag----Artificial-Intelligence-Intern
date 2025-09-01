# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FreshserviceScraper/1.0)"
}

def fetch(url, retries=3, backoff=1.0):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(backoff * (i + 1))
    raise RuntimeError("unreachable")

def extract_text_from_page(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup.find("article") or soup.find("div", class_="content") or soup.body
    if main is None:
        return "", ""
    title_tag = main.find(['h1','h2','h3']) or soup.title
    title = title_tag.get_text(strip=True) if title_tag else base_url
    parts = []
    for el in main.find_all(['h1','h2','h3','p','li','pre','code'], recursive=True):
        text = el.get_text(separator="\n", strip=True)
        if text:
            parts.append(text)
    content = "\n\n".join(parts)
    return title, content

def get_links(html, base):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    base_domain = urlparse(base).netloc
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        abs_url = urljoin(base, href)
        parsed = urlparse(abs_url)
        if parsed.netloc and base_domain in parsed.netloc and parsed.scheme in ("http", "https"):
            links.add(abs_url.split("#")[0])
    return list(links)

def scrape(start_url, out_path="data/docs.json", max_pages=200):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    to_visit = [start_url]
    visited = set()
    docs = []
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print("Scraping:", url)
        try:
            html = fetch(url)
        except Exception as e:
            print("Failed to fetch", url, e)
            visited.add(url)
            continue
        try:
            title, content = extract_text_from_page(html, url)
            docs.append({"url": url, "title": title, "content": content})
        except Exception as e:
            print("Failed to parse", url, e)
        visited.add(url)
        try:
            links = get_links(html, start_url)
            for l in links:
                if l not in visited and l not in to_visit:
                    to_visit.append(l)
        except Exception:
            pass
        time.sleep(0.5)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(docs)} pages to {out_path}")
    return docs

if __name__ == "__main__":
    START = "https://api.freshservice.com/#ticket_attributes"
    scrape(START, out_path="data/docs.json", max_pages=300)
