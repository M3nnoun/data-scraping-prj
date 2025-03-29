from playwright.sync_api import sync_playwright
import argparse
import json
import time

def scrape_movie_links(min_items):

    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to target page
            page.goto("https://www.themoviedb.org/movie/top-rated")
            print("Loaded initial page")

            # Attempt to click specified button
            try:
                button = page.wait_for_selector('xpath=//*[@id="pagination_page_1"]/p/a', timeout=5000)
                if button:
                    button.click()
                    print("Clicked pagination button")
                    time.sleep(2)
            except:
                print("Pagination button not found, continuing...")

            collected_links = []
            scroll_attempts = 0
            max_scroll_attempts = 100

            while len(collected_links) < min_items and scroll_attempts < max_scroll_attempts:
                # Scroll to bottom
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                print(f"Scrolled to bottom (attempt {scroll_attempts + 1})")
                
                # Wait for new content to load
                time.sleep(1.5)
                
                # Update link collection
                new_links = page.query_selector_all('div.card.style_1 h2 a')
                current_count = len(new_links)
                
                if current_count > len(collected_links):
                    collected_links = [
                        f"https://www.themoviedb.org{link.get_attribute('href')}"
                        for link in new_links
                    ]
                    print(f"Found {current_count} links so far")
                    scroll_attempts = 0 
                else:
                    scroll_attempts += 1

            final_links = collected_links[:min_items] if len(collected_links) >= min_items else collected_links
            
            # Save to JSON
            with open('movie_links.json', 'w') as f:
                json.dump({
                    "count": len(final_links),
                    "links": final_links
                }, f, indent=2)

            print(f"\nSuccessfully saved {len(final_links)} links to movie_links.json")
            print("Sample links:")
            for link in final_links[:3]:
                print(f" - {link}")

        finally:
            browser.close()

if __name__ == "__main__":
    scrape_movie_links()