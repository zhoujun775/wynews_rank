# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class WynewsPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_table):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_table = mongo_table

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_table=crawler.settings.get('MONGO_TABLE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.table = self.db[self.mongo_table]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if self.table.insert_one(dict(item)):
            print(">>>>>>>>>insert successfully>>>>>>>>>>>>")
        else:
            print(">>>>>>>>>insert failed>>>>>>>>>>>>>>>>>>")
        return item