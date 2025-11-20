"""
from flask import Flask 

app = Flask(__name__)

@app.route('/')
def helloUser():
    return 'Hello! Welcome to my Flask App! 🎉'

if __name__ == '__main__':
    app.run(debug=True)  """

from flask import Flask, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def fetch_cricket_update():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # run headless for API
        page = browser.new_page()

        # Step 1: Navigate to Bing
        page.goto("https://www.bing.com")

        # Step 2: Search text
        query = "SA vs AUS latest update"
        page.fill("xpath=//*[@id='sb_form_q']", query)
        page.keyboard.press("Enter")

        # Wait for search results to load with multiple fallback selectors
        page.wait_for_timeout(3000)  # Give time for results to load
        
        clicked_text = ""
        try:
            # Try modern Bing selector first
            page.wait_for_selector("h2 a", timeout=10000)
            first_link = page.locator("h2 a").first
            clicked_text = first_link.text_content()
        except:
            try:
                # Alternative selector for Bing search results
                page.wait_for_selector("[data-tag='titleLink']", timeout=5000)
                first_link = page.locator("[data-tag='titleLink']").first
                clicked_text = first_link.text_content()
            except:
                # Fallback - any link that contains cricket/sports keywords
                page.wait_for_selector("a[href*='cricket'], a[href*='sport'], a[href*='news']", timeout=5000)
                first_link = page.locator("a[href*='cricket'], a[href*='sport'], a[href*='news']").first
                clicked_text = first_link.text_content()

        # Step 3: Click the first search result
        first_link.click()

        # Step 4: Wait for the page to load
        page.wait_for_load_state("networkidle", timeout=30000)

        title = page.title()
        url = page.url

        browser.close()

        return {
            "search_query": query,
            "clicked_result_text": clicked_text,
            "page_title": title,
            "page_url": url
        }

@app.route("/cricket-update", methods=["GET"])
def cricket_update():
    try:
        result = fetch_cricket_update()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
