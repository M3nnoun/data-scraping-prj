from spider import scrape_movie_links
from get_data import scrape_movie_details
import argparse

def main():
    parser = argparse.ArgumentParser(description='TMDB Scraper')
    parser.add_argument('--min-items', type=int, default=20,
                       help='Minimum number of movies to scrape')
    args = parser.parse_args()

    print("🚀Starting link scraping...")
    link_count = scrape_movie_links(args.min_items)
    print(f"✅ Scraped {link_count} links")
    
    print("\n Starting detail scraping...")
    detail_count = scrape_movie_details()
    print(f"Scraped details for {detail_count} movies")

if __name__ == "__main__":
    main()