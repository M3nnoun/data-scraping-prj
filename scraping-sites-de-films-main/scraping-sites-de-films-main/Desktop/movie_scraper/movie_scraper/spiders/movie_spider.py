import scrapy
import re
from datetime import datetime
from scrapy.http import Request

class ImdbSpider(scrapy.Spider):
    name = "imdb_spider"
    allowed_domains = ["imdb.com"]
    # URLs de départ - plusieurs catégories de films pour maximiser la collecte
    start_urls = [
        "https://www.imdb.com/chart/top/",            # Top 250 films
        "https://www.imdb.com/chart/moviemeter/",     # Films populaires actuellement
        "https://www.imdb.com/chart/boxoffice/",      # Box-office
        # Films par genres
        "https://www.imdb.com/search/title/?genres=action",  # Action
        "https://www.imdb.com/search/title/?genres=comedy",  # Comédie
        "https://www.imdb.com/search/title/?genres=drama",   # Drame
        "https://www.imdb.com/search/title/?genres=horror",  # Horreur
        "https://www.imdb.com/search/title/?genres=thriller", # Thriller
        "https://www.imdb.com/search/title/?genres=sci-fi",   # Science-fiction
        "https://www.imdb.com/search/title/?genres=romance",  # Romance
        # Films par années
        "https://www.imdb.com/search/title/?year=2023,2023&title_type=feature",  # Films 2023
        "https://www.imdb.com/search/title/?year=2022,2022&title_type=feature",  # Films 2022
        # Films par pays
        "https://www.imdb.com/search/title/?countries=fr",  # Films français
        "https://www.imdb.com/search/title/?countries=jp",  # Films japonais
        # Films par type
        "https://www.imdb.com/search/title/?title_type=documentary",  # Documentaires
        "https://www.imdb.com/search/title/?title_type=short",        # Courts métrages
        # Films avec notes élevées
        "https://www.imdb.com/search/title/?user_rating=8.0,10.0",    # Films bien notés
    ]

    def parse(self, response):
        # Extraction des films de la page principale
        movies = response.css('li.ipc-metadata-list-summary-item')
        
        for movie in movies:
            # Extraction du titre (en supprimant le numéro de classement s'il existe)
            title_with_rank = movie.css('h3.ipc-title__text::text').get()
            title = re.sub(r'^\d+\.\s*', '', title_with_rank) if title_with_rank else None
            
            # Extraction de la note
            rating = movie.css('span.ipc-rating-star--imdb::text').get()
            
            # Obtention de l'URL de la page détaillée
            detail_url = movie.css('a.ipc-title-link-wrapper::attr(href)').get()

            if detail_url:
                # Construction de l'URL complète et envoi d'une nouvelle requête
                detail_url = response.urljoin(detail_url)
                yield Request(
                    url=detail_url,
                    callback=self.parse_movie_detail,
                    meta={'title': title, 'main_page_rating': rating}
                )

        # Pagination - passage à la page suivante si elle existe
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_movie_detail(self, response):
        # Récupération des métadonnées de la requête précédente
        title = response.meta.get('title')
        main_page_rating = response.meta.get('main_page_rating')
        
        # Extraction de l'année de sortie
        year = None
        year_elements = response.xpath('//ul[contains(@class, "ipc-inline-list")]/li[contains(@class, "ipc-inline-list__item")]/a[contains(@href, "releaseinfo")]/text()').getall()
        for element in year_elements:
            if element.strip().isdigit() and len(element.strip()) == 4:
                year = element.strip()
                break
        # Si l'année n'est pas trouvée avec la méthode précédente, essayer avec une regex
        if not year:
            year_pattern = re.compile(r'\((\d{4})\)')
            year_match = year_pattern.search(response.text)
            if year_match:
                year = year_match.group(1)
        
        # Extraction de la durée du film
        duration = None
        # Essayer d'abord la section runtime spécifique
        runtime_element = response.css('li.ipc-inline-list__item span.sc-afe43def-4::text').get()
        if runtime_element:
            duration = runtime_element.strip()
        
        # Si non trouvé, essayer avec une regex
        if not duration:
            duration_pattern = re.compile(r'(\d+)\s*hour[s]?\s*(\d+)\s*minute[s]?|(\d+)\s*h\s*(\d+)\s*m')
            duration_match = duration_pattern.search(response.text)
            if duration_match:
                groups = duration_match.groups()
                if groups[0] and groups[1]:  # Format "X heures Y minutes"
                    duration = f"{groups[0]}h {groups[1]}m"
                elif groups[2] and groups[3]:  # Format "Xh Ym"
                    duration = f"{groups[2]}h {groups[3]}m"
        
        # Extraction de la note (utiliser celle de la page détaillée si disponible)
        rating = response.css('span.ipc-rating-star--rating::text').get() or main_page_rating
        
        # Extraction des genres
        genres = response.css('div.ipc-chip-list__scroller a.ipc-chip--on-baseAlt span.ipc-chip__text::text').getall()
        genres = [g.strip() for g in genres if g.strip() != "Back to top"]

        # Extraction de la description (essayer plusieurs sélecteurs)
        description = None
        for selector in [
            'span.sc-466bb6c-2::text',
            'div.sc-16ede01-7 span::text',
            'p[data-testid="plot"] span::text',
            'div.plot_summary_wrapper div.summary_text::text'
        ]:
            desc = response.css(selector).get()
            if desc and desc.strip():
                description = desc.strip()
                break

        # Extraction des acteurs (limité aux 5 premiers)
        actors = response.css('a[data-testid="title-cast-item__actor"]::text').getall()
        actors = [a.strip() for a in actors if a.strip()][:5]

        # Extraction du réalisateur
        director = response.xpath('//a[@data-testid="title-pc-principal-credit"]/text()').get()
        if not director:
            director_section = response.xpath('//span[contains(text(), "Director") or contains(text(), "Directors")]/following-sibling::div[1]//a/text()').get()
            if director_section:
                director = director_section.strip()

        # Construction et retour de l'objet film complet
        yield {
            'source': 'imdb',
            'title': title,
            'year': year,
            'duration': duration,
            'rating': rating.strip() if rating else None,
            'genres': genres,
            'description': description,
            'actors': actors,
            'director': director,
            'url': response.url,
            'scraped_at': datetime.now().isoformat()
        }

