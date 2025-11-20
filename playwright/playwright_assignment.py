from playwright.sync_api import sync_playwright
import time, json

URL = "https://colab.research.google.com"
OUT_TEXT = "page_text.txt"
OUT_META = "page_metadata.json"

def auto_scroll(page, steps=40, pause=0.3):
    for _ in range(steps):
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(pause)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(URL, timeout=60000)
    time.sleep(3)
    auto_scroll(page)

    # Extract visible text
    try:
        text = page.inner_text("body")
    except:
        text = page.evaluate("document.body.innerText")

    with open(OUT_TEXT, "w", encoding="utf-8") as f:
        f.write(text)

    # Extract metadata
    title = page.title()

    description = page.evaluate("""
        () => document.querySelector('meta[name="description"]')?.content || ""
    """)

    keywords = page.evaluate("""
        () => document.querySelector('meta[name="keywords"]')?.content || ""
    """)

    headings = page.evaluate("""
        () => Array.from(document.querySelectorAll("h1, h2, h3, h4, h5, h6"))
            .map(h => ({ tag: h.tagName, text: h.innerText.trim() }))
    """)

    links = page.evaluate("""
        () => Array.from(document.querySelectorAll("a[href]"))
            .map(a => ({ text: a.innerText.trim(), href: a.href }))
    """)

    images = page.evaluate("""
        () => Array.from(document.querySelectorAll("img"))
            .map(img => img.src)
    """)

    metadata = {
        "title": title,
        "description": description,
        "keywords": keywords,
        "headings": headings,
        "links": links,
        "images": images
    }

    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Saved text to {OUT_TEXT}")
    print(f"✅ Saved metadata to {OUT_META}")

    browser.close()
