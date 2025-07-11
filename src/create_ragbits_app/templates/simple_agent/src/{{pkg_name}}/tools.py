import requests
from markdownify import markdownify as md
from bs4 import BeautifulSoup


def get_yahoo_finance_markdown() -> str:
    """
    Download content from Yahoo Finance homepage and return it as markdown string.

    Returns:
        str: Markdown formatted content from Yahoo Finance
    """
    url = "https://finance.yahoo.com/"

    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        main_container = soup.find(class_="mainContainer")

        if not main_container:
            return "Error: mainContainer not found on the page"

        for element in main_container(["script", "style", "noscript", "meta", "head"]):
            element.decompose()

        markdown_content = md(
            str(main_container),
            heading_style="ATX",
            bullets="-",
            strip=['script', 'style', 'meta', 'head', 'title'],
            autolinks=True,
            escape_misc=False,
            wrap=True,
            wrap_width=80
        )

        return markdown_content

    except requests.RequestException as e:
        return f"Error fetching content: {e}"
    except Exception as e:
        return f"Error processing content: {e}"
