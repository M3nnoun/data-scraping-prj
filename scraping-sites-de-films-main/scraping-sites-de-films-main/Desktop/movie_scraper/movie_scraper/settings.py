
BOT_NAME = 'movie_scraper'

SPIDER_MODULES = ['movie_scraper.spiders']
NEWSPIDER_MODULE = 'movie_scraper.spiders'

# Respectez les règles robots.txt
ROBOTSTXT_OBEY = True

# Configurez un délai entre les requêtes pour ne pas surcharger les serveurs
DOWNLOAD_DELAY = 2

# Configurez des user agents aléatoires pour éviter d'être bloqué
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

# Configurez les pipelines
ITEM_PIPELINES = {
    'movie_scraper.pipelines.MovieScraperPipeline': 300,
    #'movie_scraper.pipelines.MongoPipeline': 400,
}

# Configuration MongoDB
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'movie_scraper'

# Configuration des proxies si nécessaire
# PROXY_POOL_ENABLED = True
