import datetime
import email.utils
import logging
import re
import time
from urllib.parse import urlparse
import feedparser
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def clean_html(text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_url(url: str) -> str:
    """Normalizes URL by stripping query parameters and trailing slashes for deduplication."""
    try:
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if normalized.endswith("/"):
            normalized = normalized[:-1]
        return normalized
    except Exception:
        return url


def parse_rss_feed(feed_url: str, limit_days: int) -> list[dict]:
    """Parses an RSS feed and returns items within the limit_days."""
    logger.info(f"Parsing RSS feed: {feed_url}")
    results = []
    now = datetime.datetime.now(datetime.timezone.utc)

    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            snippet = (
                entry.get("summary", "")
                or entry.get("description", "")
                or entry.get("content", [{"value": ""}])[0].get("value", "")
            )

            title = clean_html(title)
            snippet = clean_html(snippet)

            pub_date = None
            if "published_parsed" in entry and entry.published_parsed:
                pub_date = datetime.datetime(
                    *entry.published_parsed[:6], tzinfo=datetime.timezone.utc
                )
            elif "updated_parsed" in entry and entry.updated_parsed:
                pub_date = datetime.datetime(
                    *entry.updated_parsed[:6], tzinfo=datetime.timezone.utc
                )
            elif "published" in entry:
                try:
                    pub_date = email.utils.parsedate_to_datetime(entry.published)
                except Exception:
                    pass

            if pub_date:
                age_days = (now - pub_date).days
                if age_days > limit_days:
                    continue

            results.append(
                {
                    "title": title,
                    "url": link,
                    "snippet": snippet[:200]
                    + ("..." if len(snippet) > 200 else ""),
                    "source": "RSS Feed",
                    "date": pub_date.strftime("%Y-%m-%d")
                    if pub_date
                    else "N/A",
                }
            )
    except Exception as e:
        logger.error(f"Error parsing RSS feed {feed_url}: {e}")

    return results


def fetch_news_via_ddg(query: str, limit_days: int) -> list[dict]:
    """Performs a DuckDuckGo search for a given query and returns recent news items."""
    logger.info(f"Searching DuckDuckGo for: {query}")
    results = []
    timelimit = "d" if limit_days <= 1 else "w"

    try:
        with DDGS() as ddgs:
            ddg_results = ddgs.text(
                query,
                region="jp-jp",
                safesearch="moderate",
                timelimit=timelimit,
                max_results=10,
            )

            if ddg_results:
                for r in ddg_results:
                    title = clean_html(r.get("title", ""))
                    url = r.get("href", "")
                    snippet = clean_html(r.get("body", ""))
                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "Web Search",
                            "date": "Recent",
                        }
                    )
    except Exception as e:
        logger.error(f"Error searching DuckDuckGo for '{query}': {e}")
        time.sleep(1)

    return results


def search_all_news(limit_days: int) -> list[dict]:
    """Collects and aggregates news from RSS feeds and DuckDuckGo searches."""
    all_items = []
    seen_urls = set()

    # 1. Gather from RSS feeds (high reliability)
    rss_feeds = [
        ("Zenn (AI Topic)", "https://zenn.dev/topics/ai/feed"),
        ("Zenn (Notion Topic)", "https://zenn.dev/topics/notion/feed"),
        ("ジェネトピ", "https://note.com/genai_topic/rss"),
        ("AGIラボ", "https://chatgpt-lab.com/feed"),
    ]

    for name, url in rss_feeds:
        feed_items = parse_rss_feed(url, limit_days)
        for item in feed_items:
            item["source"] = name
            norm_url = normalize_url(item["url"])
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                all_items.append(item)

    # 2. Gather from DuckDuckGo search queries
    search_queries = [
        'site:notion.so/blog OR site:notion.so/help/whats-new "Notion"',
        '"生成AI" (ニュース OR アップデート)',
        '"Notion AI" (機能 OR ニュース OR 使い方)',
        '"AIエージェント" (開発 OR 動向 OR 発表)',
        'site:openai.com/news "GPT" OR "OpenAI"',
        'site:blog.google "Gemini" OR "Google AI"',
        'site:news.microsoft.com "Copilot" OR "Microsoft"',
        'site:news.yahoo.co.jp "生成AI"',
    ]

    for query in search_queries:
        search_items = fetch_news_via_ddg(query, limit_days)
        for item in search_items:
            url = item["url"]
            if "openai.com" in url:
                item["source"] = "OpenAI (公式)"
            elif "blog.google" in url or "deepmind.google" in url:
                item["source"] = "Google (公式)"
            elif "microsoft.com" in url:
                item["source"] = "Microsoft News (公式)"
            elif "notion.so" in url or "notion.com" in url:
                item["source"] = "Notion (公式)"
            elif "yahoo.co.jp" in url:
                item["source"] = "Yahoo!ニュース"
            elif "zenn.dev" in url:
                item["source"] = "Zenn"
            elif "chatgpt-lab.com" in url:
                item["source"] = "AGIラボ"
            elif "note.com/genai_topic" in url:
                item["source"] = "ジェネトピ"

            norm_url = normalize_url(url)
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                all_items.append(item)

    logger.info(
        f"Search completed. Found {len(all_items)} unique news items in total."
    )
    return all_items


if __name__ == "__main__":
    print("Testing searcher...")
    items = search_all_news(limit_days=3)
    print(f"Retrieved {len(items)} items:")
    for idx, item in enumerate(items[:5]):
        print(f"{idx+1}. [{item['source']}] {item['title']} - {item['url']}")
