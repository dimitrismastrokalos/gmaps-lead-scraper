import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_gmaps_lite(search_query, max_results=10):
    print(f"🔎 Searching for: {search_query}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # Scroll down results panel
        try:
            await page.hover('div[role="feed"]')
            for _ in range(3):
                await page.mouse.wheel(0, 1000)
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        results = []
        listings = await page.locator('a[href*="/maps/place/"]').all()

        for listing in listings:
            if len(results) >= max_results:
                break
            try:
                title = await listing.get_attribute('aria-label')
                link = await listing.get_attribute('href')
                if title and title not in [r["Name"] for r in results]:
                    results.append({"Name": title, "Link": link})
            except Exception:
                continue

        await browser.close()
        
        # Save output to CSV
        with open("leads_lite.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Link"])
            writer.writeheader()
            writer.writerows(results)

        print(f"✅ Found {len(results)} results! Saved to leads_lite.csv")

if __name__ == "__main__":
    asyncio.run(scrape_gmaps_lite("gyms in athens", max_results=10))