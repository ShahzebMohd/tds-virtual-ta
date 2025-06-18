import json
import html2text
from tqdm import tqdm
from playwright.sync_api import sync_playwright

BASE_URL = "https://tds.s-anand.net/"
OUTPUT_FILE = "tds_course_content.json"

def scrape_docsify_site():
    scraped = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # use False for debugging visually
        page = browser.new_page()
        print("🌐 Loading site...")
        page.goto(BASE_URL)
        page.wait_for_timeout(5000)  # wait for sidebar + JS

        print("🔗 Extracting sidebar links...")
        sidebar_links = page.query_selector_all('.sidebar a[href^="#/"]')
        print(f"✅ Found {len(sidebar_links)} sidebar links.\n")

        for i, link in enumerate(tqdm(sidebar_links)):
            try:
                href = link.get_attribute('href')
                title = link.get_attribute('title') or link.inner_text().strip()

                if href and href.startswith("#/") and href not in seen:
                    seen.add(href)

                    # Click the link
                    page.click(f'a[href="{href}"]')
                    page.wait_for_timeout(2000)  # wait for content to load

                    # Extract content from <main>
                    html = page.locator("main").inner_html()
                    markdown = html2text.html2text(html)

                    scraped.append({
                        "title": title,
                        "url": BASE_URL + href,
                        "content": markdown.strip()
                    })
            except Exception as e:
                print(f"⚠️ Error processing link {i}: {e}")

        browser.close()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(scraped)} pages. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_docsify_site()
