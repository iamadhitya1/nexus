import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def _fetch(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            html = await page.content()
        except Exception:
            html = ""
        await browser.close()
    return html


def read_url(url: str, max_chars: int = 4000) -> str:
    """
    Visit a URL and return its cleaned text content.
    """
    try:
        html = asyncio.run(_fetch(url))
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = " ".join(text.split())
        return text[:max_chars]
    except Exception as e:
        return f"Could not read URL: {e}"
