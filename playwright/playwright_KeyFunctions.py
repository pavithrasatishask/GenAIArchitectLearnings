from playwright.async_api import async_playwright
import asyncio


async def playwright_function():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        pages = await browser.new_page()
        await pages.goto('https://www.google.com')
        await pages.wait_for_timeout(1000)  # Wait for 1 seconds to see the page
        #title = await pages.title()
        #print(f'Page title: {title}')

        #[@id="_-6wMaYaOCMSP-d8PmpnegQo_37"]
        await browser.close()

if __name__ == "__main__":
    asyncio.run(playwright_function())