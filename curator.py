import datetime
import json
import logging
import time
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field
import config

logger = logging.getLogger(__name__)


class NewsItem(BaseModel):
    title: str = Field(
        description="厳選されたニュース記事のタイトル。日本語で分かりやすい表現に整えてください。"
    )
    url: str = Field(description="記事の正確なURL。")
    source: str = Field(
        description="ニュースのソース名またはカテゴリ。例: Notion (公式), OpenAI (公式), Google (公式), Microsoft News (公式), Zenn, Yahoo!ニュース, AGIラボ, ジェネトピ など。"
    )
    summary: list[str] = Field(
        description="記事の内容についての分かりやすい日本語の要約。必ず3つの箇条書きにしてください。"
    )
    importance_reason: str = Field(
        description="このニュースを選定した理由を説明する日本語。"
    )


class CuratedNews(BaseModel):
    articles: list[NewsItem] = Field(
        description="収集されたニュースの中から厳選した、重要度の高い上位10件のニュースリスト。"
    )


def get_badge_styles(source: str) -> tuple[str, str]:
    """Returns (text_color, bg_color) based on the source name for custom badges."""
    source_lower = source.lower()
    if "notion" in source_lower:
        return "#000000", "#F3F4F6"
    elif "openai" in source_lower or "chatgpt" in source_lower:
        return "#10B981", "#E6F4EA"
    elif "google" in source_lower:
        return "#1A73E8", "#E8F0FE"
    elif "microsoft" in source_lower:
        return "#F59E0B", "#FFF7E6"
    elif "zenn" in source_lower:
        return "#3EA8FF", "#EBF5FF"
    elif "qiita" in source_lower:
        return "#55C500", "#EAF8E6"
    elif "itmedia" in source_lower:
        return "#D32F2F", "#FFEBEE"
    elif "はてな" in source_lower or "hatena" in source_lower:
        return "#00A4DE", "#E6F6FC"
    elif "agi" in source_lower or "ジェネトピ" in source_lower:
        return "#8B5CF6", "#F5F3FF"
    elif "yahoo" in source_lower:
        return "#FF0033", "#FFF0F2"
    else:
        return "#4B5563", "#F3F4F6"


def build_html_email(articles: list) -> str:
    """Builds a premium HTML email template with curated news articles."""
    jst = datetime.timezone(datetime.timedelta(hours=9))
    today = datetime.datetime.now(jst).strftime("%Y年%m月%d日")

    articles_html = ""
    for idx, art in enumerate(articles):
        title = art.get("title", "")
        url = art.get("url", "")
        source = art.get("source", "Web Search")
        summary_list = art.get("summary", [])
        reason = art.get("importance_reason", "")

        badge_text_color, badge_bg_color = get_badge_styles(source)

        bullets = ""
        for bullet in summary_list:
            bullets += f"<li>{bullet}</li>"

        articles_html += f"""
        <!-- Article Card {idx+1} -->
        <div class="card">
          <div class="card-header">
            <span class="badge" style="color: {badge_text_color}; background-color: {badge_bg_color};">{source}</span>
            <span class="card-rank">#{idx+1}</span>
          </div>
          <h3 class="card-title">
            <a href="{url}" target="_blank">{title}</a>
          </h3>
          <ul class="card-summary">
            {bullets}
          </ul>
          {f'<div class="card-reason"><strong>選定理由:</strong> {reason}</div>' if reason else ''}
          <div style="margin-top: 15px; text-align: right;">
            <a href="{url}" target="_blank" class="read-more-btn">記事を読む →</a>
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI & Notion Morning Briefing</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: #f3f4f6;
      color: #1f2937;
      margin: 0;
      padding: 0;
      line-height: 1.6;
    }}
    .email-container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #ffffff;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}
    .header {{
      background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
      color: #ffffff;
      padding: 35px 25px;
      text-align: center;
      border-bottom: 4px solid #8b5cf6;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.025em;
    }}
    .header p {{
      margin: 8px 0 0 0;
      font-size: 14px;
      color: #c7d2fe;
    }}
    .content {{
      padding: 25px;
    }}
    .intro {{
      font-size: 15px;
      color: #4b5563;
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 1px solid #e5e7eb;
    }}
    .card {{
      background-color: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 25px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}
    .badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: inline-block;
    }}
    .card-rank {{
      font-size: 14px;
      font-weight: 800;
      color: #9ca3af;
    }}
    .card-title {{
      margin: 0 0 12px 0;
      font-size: 18px;
      font-weight: 700;
      line-height: 1.4;
    }}
    .card-title a {{
      color: #111827;
      text-decoration: none;
    }}
    .card-title a:hover {{
      color: #4f46e5;
      text-decoration: underline;
    }}
    .card-summary {{
      margin: 0 0 15px 0;
      padding-left: 20px;
      font-size: 14px;
      color: #374151;
    }}
    .card-summary li {{
      margin-bottom: 6px;
    }}
    .card-reason {{
      font-size: 12px;
      color: #4f46e5;
      background-color: #f5f3ff;
      border-left: 3px solid #8b5cf6;
      padding: 8px 12px;
      border-radius: 0 6px 6px 0;
      margin-top: 10px;
    }}
    .read-more-btn {{
      font-size: 12px;
      font-weight: 600;
      color: #4f46e5;
      text-decoration: none;
    }}
    .read-more-btn:hover {{
      text-decoration: underline;
    }}
    .footer {{
      background-color: #f9fafb;
      padding: 25px;
      text-align: center;
      font-size: 12px;
      color: #6b7280;
      border-top: 1px solid #e5e7eb;
    }}
    .footer p {{
      margin: 5px 0;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>AI & Notion Morning Briefing</h1>
      <p>{today} | 本日の厳選トピックス</p>
    </div>
    <div class="content">
      <div class="intro">
        おはようございます。本日（{today}）収集した生成AI・Notion関連の最新ニュースから、特に重要度の高い10件を厳選してお届けします。
      </div>
      {articles_html}
    </div>
    <div class="footer">
      <p>このメールは AI & Notion ニュース自動配信システム によって自動生成されています。</p>
      <p>© {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).year} AI & Notion News Mailer. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""
    return html


def call_gemini_with_retry(
    client: genai.Client, model: str, contents: str, schema: type
) -> str:
    """Calls Gemini API with retry logic for 503 errors."""
    max_retries = 3
    retry_delay = 20

    for attempt in range(max_retries + 1):
        try:
            logger.info(
                f"Calling Gemini API using model {model} (Attempt {attempt + 1}/{max_retries + 1})..."
            )
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2,
                ),
            )
            return response.text
        except errors.APIError as e:
            # Check if it is a 503 error
            # errors.APIError has e.code (status code) or we check the message
            status_code = getattr(e, "code", None)
            is_503 = status_code == 503 or "503" in str(e)

            if is_503 and attempt < max_retries:
                logger.warning(
                    f"503 Service Unavailable encountered. Waiting {retry_delay} seconds before retrying..."
                )
                time.sleep(retry_delay)
            else:
                logger.error(f"Gemini APIError: {e}")
                raise e
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            raise e

    raise RuntimeError("Failed to get response after max retries due to 503")


def curate_and_generate_html(raw_items: list[dict]) -> tuple[str, list[dict]]:
    """Curates collected news using gemini-3.5-flash (with retry and fallback to

    gemini-2.5-flash-lite) and generates a stylized HTML email body.
    """
    if not raw_items:
        logger.warning("No raw news items to curate.")
        return "", []

    # Prepare input content
    formatted_items = []
    for idx, item in enumerate(raw_items):
        formatted_items.append(
            f"ID: {idx}\n"
            f"Title: {item['title']}\n"
            f"Source: {item['source']}\n"
            f"URL: {item['url']}\n"
            f"Snippet: {item['snippet']}\n"
            f"---"
        )
    items_text = "\n".join(formatted_items)

    prompt = f"""
あなたは生成AIおよびNotionのエキスパートキュレーターです。
以下に収集された最近のニュース記事の一覧（タイトル、ソース、スニペットなど）があります。
この中から、ユーザーにとって【重要度が最も高いニュース 10件】を厳選し、日本語で見出し・要約・選定理由を整理してください。

【厳選のための選定基準（優先順位）】
1. **Notion公式アップデート・Notion AI関連**:
   Notion公式からの機能リリースや重要な仕様変更は最優先（重要度最大）。
2. **主要ベンダーの生成AI公式リリース（一次ソース）**:
   OpenAI、Google、Microsoftの公式リリース情報。
3. **AIエージェント関連のニュース**:
   エージェント開発、フレームワーク、実務活用の動向。
4. **信頼できる解説記事・技術解説**:
   Zenn、AGIラボ、ジェネトピ等での、最新機能の解説や実務に直結するAI活用例。
5. **一般ニュース (Yahoo!ニュース等)**:
   世間的なインパクトが大きいAI関連ニュース。

【重要ルール】
- **重複の排除**: 酷似している記事や同じ発表に対する複数メディアの報道は、最も信頼できる一次ソース（公式サイト）または内容が充実している方を1件だけ選んでください。
- **件数制限**: 必ず【ちょうど10件】を厳選してください。
- **日本語要約**: 各ニュースの要約は【3つの箇条書き】で作成し、分かりやすく具体的な内容にしてください。
- **最新優先**: できるだけ直近の新しい情報（スニペットから推測されるもの）を優先してください。
- **ソースの多様性の確保**: 厳選する10件のニュースが特定のソース（例: Zennなど）に偏らないようにしてください。特に、Zenn（「Zenn (AI Topic)」や「Zenn (Notion Topic)」など）からの選定は【最大でも3件まで】とし、Qiita、ITmedia NEWS、公式サイト（Notion, OpenAI, Google, Microsoft）、Yahoo!ニュースなど、多様なソースから幅広くピックアップしてください。

【収集されたニュース一覧】
{items_text}
"""

    # Set a timeout (120,000ms = 120s) to prevent infinite hanging during API issues
    client = genai.Client(
        api_key=config.GEMINI_API_KEY,
        http_options={"timeout": 120000}
    )
    response_text = None

    try:
        # Try gemini-3.5-flash first with retries
        response_text = call_gemini_with_retry(
            client=client,
            model="gemini-3.5-flash",
            contents=prompt,
            schema=CuratedNews,
        )
    except Exception as e:
        logger.warning(
            f"Failed with gemini-3.5-flash after retries. Falling back to gemini-2.5-flash-lite..."
        )
        try:
            # Fallback to gemini-2.5-flash-lite
            response_text = call_gemini_with_retry(
                client=client,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                schema=CuratedNews,
            )
        except Exception as fallback_err:
            logger.error(
                f"Fallback model gemini-2.5-flash-lite also failed: {fallback_err}"
            )
            return "", []

    if not response_text:
        return "", []

    try:
        curated_data = json.loads(response_text)
        articles = curated_data.get("articles", [])
        if not articles:
            logger.warning("No articles returned in the curated data JSON.")
            return "", []

        # Log selection
        logger.info(f"Successfully curated {len(articles)} articles:")
        for idx, art in enumerate(articles):
            logger.info(f"  #{idx+1}: [{art.get('source')}] {art.get('title')}")

        # Build HTML
        return build_html_email(articles), articles

    except Exception as e:
        logger.error(f"Error parsing Gemini JSON response: {e}")
        return "", []
