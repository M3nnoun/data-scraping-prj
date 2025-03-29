from playwright.sync_api import sync_playwright
import json
import time
import re

def safe_extract(locator, attribute=None, default="N/A"):
    try:
        if locator.count() > 0:
            return locator.get_attribute(attribute) if attribute else locator.first.inner_text().strip()
        return default
    except:
        return default

def scrape_movie_details():
    try:
        with open('movie_links.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            urls = data['links']
    except FileNotFoundError:
        print("Run links scraper first!")
        return []

    all_movies = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in urls:
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector('.header.large.border.first', timeout=15000)

                movie_data = {
                    'title': safe_extract(page.locator('.title h2 a')),
                    'year': safe_extract(page.locator('.tag.release_date'), default="").strip('()'),
                    'score': safe_extract(page.locator('.user_score_chart'), 'data-percent'),
                    'poster': safe_extract(page.locator('.poster img'), 'src'),
                    'genres': [a.inner_text() for a in page.locator('span.genres a').all()],
                    'directors': [],
                    'runtime': safe_extract(page.locator('span.runtime')),
                    'url': url
                }

                # Director extraction
                for profile in page.locator('.people li.profile').all():
                    if 'Director' in safe_extract(profile.locator('.character')):
                        movie_data['directors'].append({
                            'name': safe_extract(profile.locator('p a')),
                            'role': safe_extract(profile.locator('.character'))
                        })

                all_movies.append(movie_data)
                
            except Exception as e:
                print(f"Failed {url}: {str(e)}")
                continue
            
            time.sleep(1)

        browser.close()
    
    # Save final results
    with open('movie_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, indent=2, ensure_ascii=False)
    
    return len(all_movies)