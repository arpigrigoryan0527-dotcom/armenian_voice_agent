import asyncio
import json
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BANK_URLS = {
    "Ameriabank": {
        "credits": [
            "https://ameriabank.am/personal/loans",
        ],
        "deposits": [
            "https://ameriabank.am/personal/deposits",
        ],
        "branches": [
            "https://ameriabank.am/personal/branches-and-atms",
        ]
    },
    "Ardshinbank": {
        "credits": [
            "https://ardshinbank.am/for-you/loans-ardshinbank?lang=hy",
        ],
        "deposits": [
            "https://ardshinbank.am/for-you/avand?lang=hy",
        ],
        "branches": [
            "https://ardshinbank.am/Information/branch-atm?lang=hy",
        ]
    },
    "Acba": {
        "credits": [
            "https://www.acba.am/hy/individuals/loans/consumer-credits",
        ],
        "deposits": [
            "https://www.acba.am/hy/individuals/save-and-invest/deposits",
        ],
        "branches": [
            "https://www.acba.am/hy/contacts",
        ]
    }
}

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    return soup

def extract_data(soup):
    results = []
    
    # Սահմանում ենք այն թեգերը, որոնք սովորաբար պարունակում են բովանդակային տեքստ
    content_tags = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'table'])

    for tag in content_tags:
        # Մաքրում ենք տեքստը ավելորդ բացատներից
        text = tag.get_text(separator=" ", strip=True)
        
        # Ֆիլտրում ենք շատ կարճ տողերը
        if len(text) > 30:
            results.append({
                "text": text,
                "type": tag.name  # Պահում ենք թեգի տեսակը
            })

    return results

async def auto_scroll(page):
    """Scroll to bottom to load dynamic content"""
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 500;
                let timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    if (totalHeight >= document.body.scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 300);
            });
        }
    """)

async def scrape_page(page, url):
    try:
        print(f"    → Opening {url}")

        # STEP 1: open page
        await page.goto(url, timeout=120000, wait_until="domcontentloaded")

        # STEP 2: wait a bit for JS
        await page.wait_for_timeout(4000)

        # STEP 3: scroll
        await auto_scroll(page)

        # STEP 4: extra wait after scroll
        await page.wait_for_timeout(3000)

        # STEP 5: get HTML
        html = await page.content()
        soup = clean_html(html)

        # STEP 6: extract structured data
        data = extract_data(soup)

        # Fallback եթե ոչինչ չի գտնվել
        if not data:
            print("    ⚠️ No structured data, fallback to raw text")
            text = soup.get_text(separator="\n", strip=True)
            lines = [l for l in text.splitlines() if len(l) > 40]
            data = [{"text": l} for l in lines[:20]]

        print(f"    ✅ Extracted {len(data)} items")
        return data

    except Exception as e:
        print(f"    ❌ Error: {e}")
        return []

async def main():
    data = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for bank, categories in BANK_URLS.items():
            print(f"\n🏦 {bank}")
            data[bank] = {}

            for category, urls in categories.items():
                all_items = []

                for url in urls:
                    items = await scrape_page(page, url)

                    for item in items:
                        all_items.append({
                            "bank": bank,
                            "category": category,
                            "url": url,
                            **item
                        })

                data[bank][category] = all_items
                print(f"  📦 Total: {len(all_items)} items")

        await browser.close()

    with open("final_bank_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n✅ DONE")

if __name__ == "__main__":
    asyncio.run(main())