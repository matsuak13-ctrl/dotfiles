import logging
import sys
import config
from curator import curate_and_generate_html
from mailer import send_html_email
from searcher import search_all_news
from gdocs_writer import append_articles_to_gdoc

# Setup logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== Starting AI & Notion News Mailer (Re-implemented) ===")

    # 1. Validate environment configuration
    valid, errors = config.validate_config()
    if not valid:
        logger.error("Configuration validation failed:")
        for err in errors:
            logger.error(f"  - {err}")
        logger.error(
            "Please configure the .env file with valid credentials. Exiting."
        )
        sys.exit(1)

    # 2. Search for raw news items
    logger.info(
        f"Step 1: Searching for news (limit days: {config.SEARCH_LIMIT_DAYS})..."
    )
    raw_news = search_all_news(limit_days=config.SEARCH_LIMIT_DAYS)

    if not raw_news:
        logger.warning(
            "No news items were found during the search. Cannot proceed."
        )
        sys.exit(0)

    logger.info(f"Successfully collected {len(raw_news)} unique news items.")

    # 3. Curate, summarize and generate HTML body using Gemini API
    logger.info("Step 2: Curating top 10 news and generating HTML body...")
    html_body, articles = curate_and_generate_html(raw_news)

    if not html_body:
        logger.error(
            "HTML email body generation failed (Gemini returned empty or error). Exiting."
        )
        sys.exit(1)

    logger.info("HTML email body successfully generated.")

    # 4. Send the email
    logger.info("Step 3: Sending HTML newsletter via Gmail SMTP...")
    success = send_html_email(html_body)

    if success:
        logger.info("Email sent successfully. Now archiving news to Google Doc...")
        
        # 5. Archive to Google Doc for NotebookLM sync
        doc_success = append_articles_to_gdoc(articles)
        if doc_success:
            logger.info("Successfully archived news to Google Doc.")
        else:
            logger.warning("Could not archive news to Google Doc (check credentials or document ID).")

        logger.info(
            "=== AI & Notion News Mailer execution completed successfully! ==="
        )
    else:
        logger.error("=== AI & Notion News Mailer execution failed. ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
