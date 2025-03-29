# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
    
from scrapy.exceptions import DropItem
import pymongo

class MovieScraperPipeline:
    def process_item(self, item, spider):
        # Vérification des données obligatoires
        if not item.get('title'):
            raise DropItem("Film sans titre trouvé")
        return item

class MongoPipeline:
    collection_name = 'movies'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'movie_scraper')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Vérification si le film existe déjà
        existing = self.db[self.collection_name].find_one({'title': item['title'], 'source': item['source']})
        
        if existing:
            # Mise à jour du film existant
            self.db[self.collection_name].update_one(
                {'_id': existing['_id']},
                {'$set': dict(item)}
            )
        else:
            # Insertion d'un nouveau film
            self.db[self.collection_name].insert_one(dict(item))
        
        return item
