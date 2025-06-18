import requests
import json
from bs4 import BeautifulSoup

def scrape_discourse(start_id=150000, end_id=160000):
    base_url = "https://discourse.onlinedegree.iitm.ac.in/t/"
    posts = []

    for post_id in range(start_id, end_id):
        try:
            url = f"{base_url}{post_id}"
            res = requests.get(url)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            title_tag = soup.find("title")
            post_body = soup.find("div", class_="cooked")

            if title_tag and post_body:
                posts.append({
                    "id": post_id,
                    "title": title_tag.text.strip(),
                    "content": post_body.text.strip(),
                    "url": url
                })

        except Exception as e:
            print(f"Error at {post_id}: {e}")

    with open("data/discourse.json", "w") as f:
        json.dump(posts, f, indent=2)

if __name__ == "__main__":
    scrape_discourse(155000, 155050)  # small range for demo

