import json
from playwright.sync_api import sync_playwright
from time import sleep

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_URL = f"{BASE_URL}/c/courses/tds-kb/34"

OUTPUT_FILE = "data/tds_discourse.json"

def scrape_discourse():
    all_posts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"🌐 Loading TDS Discourse category...")
        page.goto(CATEGORY_URL)
        page.wait_for_timeout(5000)

        # Scroll to load more posts
        print("🔄 Scrolling to load posts...")
        for _ in range(20):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(1000)

        # Wait until topics are visible
        page.wait_for_selector("a.title")

        topic_elements = page.query_selector_all("a.title")
        topic_links = []

        for el in topic_elements:
            href = el.get_attribute("href")
            title = el.inner_text().strip()
            if href and title:
                full_url = href if href.startswith("http") else BASE_URL + href
                topic_links.append({
                    "title": title,
                    "url": full_url
                })

        print(f"✅ Found {len(topic_links)} topics.")

        for link in topic_links:
            try:
                print(f"🔍 Scraping: {link['title']}")
                page.goto(link['url'])
                page.wait_for_timeout(3000)
                page.wait_for_selector('.cooked')  # ✅ wait for post content to appear

                posts = page.query_selector_all('.cooked')
                texts = [p.inner_text().strip() for p in posts if p.inner_text().strip()]

                all_posts.append({
                    "title": link["title"],
                    "url": link["url"],  # ✅ corrected from 'href'
                    "content": "\n\n---\n\n".join(texts)
                })

            except Exception as e:
                print(f"⚠️ Failed: {link.get('url', 'UNKNOWN')} | {e}")
                continue

        browser.close()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"\n✅ Scraped {len(all_posts)} posts → saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_discourse()

