import datetime
import logging
import requests
import config

logger = logging.getLogger(__name__)


def append_articles_to_gdoc(articles: list[dict]) -> bool:
    """Appends curated news articles to the specified Google Document via GAS Web App.

    Args:
        articles (list[dict]): A list of dictionary objects representing news articles.

    Returns:
        bool: True if appended successfully, False otherwise.
    """
    if (
        not config.GAS_WEBAPP_URL
        or config.GAS_WEBAPP_URL == "your_gas_webapp_url_here"
    ):
        logger.warning(
            "GAS_WEBAPP_URL is not configured. Skipping Google Docs archiving."
        )
        return False

    if (
        not config.GOOGLE_DOC_ID
        or config.GOOGLE_DOC_ID == "your_google_doc_id_here"
    ):
        logger.warning(
            "GOOGLE_DOC_ID is not configured. Skipping Google Docs archiving."
        )
        return False

    jst = datetime.timezone(datetime.timedelta(hours=9))
    today_str = datetime.datetime.now(jst).strftime("%Y年%m月%d日")

    # Format the content to append as a clean structured text
    text_to_append = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text_to_append += f"■ {today_str} AI & Notion News\n"
    text_to_append += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for idx, art in enumerate(articles):
        title = art.get("title", "")
        url = art.get("url", "")
        source = art.get("source", "Web Search")
        summary_list = art.get("summary", [])
        reason = art.get("importance_reason", "")

        text_to_append += f"#{idx+1} [{source}] {title}\n"
        if url:
            text_to_append += f"URL: {url}\n"
        for bullet in summary_list:
            text_to_append += f"・ {bullet}\n"
        if reason:
            text_to_append += f"【選定理由】: {reason}\n"
        text_to_append += "\n"

    try:
        logger.info(f"Sending payload to GAS Web App: {config.GAS_WEBAPP_URL}")
        payload = {
            "docId": config.GOOGLE_DOC_ID,
            "text": text_to_append,
            "token": config.GAS_ACCESS_TOKEN,
        }

        response = requests.post(
            config.GAS_WEBAPP_URL, json=payload, timeout=30
        )

        # Check HTTP response code
        response.raise_for_status()

        # Parse JSON response from GAS
        result = response.json()
        if result.get("status") == "success":
            logger.info(
                "Successfully appended curated news to Google Doc via GAS Web App!"
            )
            return True
        else:
            logger.error(f"GAS Web App reported an error: {result.get('message')}")
            return False

    except Exception as e:
        logger.error(f"Failed to send news to GAS Web App: {e}")
        return False
