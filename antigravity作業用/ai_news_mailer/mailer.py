import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

logger = logging.getLogger(__name__)


def send_html_email(html_body: str) -> bool:
    """Sends the HTML news briefing via Gmail SMTP.

    Args:
        html_body (str): The HTML string representing the email content.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    logger.info("Preparing to send curated newsletter email...")

    if not html_body:
        logger.warning("Empty HTML body. Aborting email sending.")
        return False

    today_str = datetime.datetime.now().strftime("%Y/%m/%d")

    # Set up email headers
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"【AI & Notion 朝刊】{today_str} の厳選ニュース5選"
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.RECIPIENT_ADDRESS

    # Attach HTML content
    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(html_part)

    try:
        logger.info("Connecting to Gmail SMTP server via SSL (port 465)...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            logger.info("Logging in to Gmail SMTP...")
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            logger.info(
                f"Sending email from {config.GMAIL_ADDRESS} to {config.RECIPIENT_ADDRESS}..."
            )
            server.sendmail(
                config.GMAIL_ADDRESS, config.RECIPIENT_ADDRESS, msg.as_string()
            )
            logger.info("Email sent successfully!")
            return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
