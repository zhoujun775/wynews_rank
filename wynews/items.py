# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WynewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    time = scrapy.Field()
    comment_num = scrapy.Field()
    clicks_num = scrapy.Field()
    spider_time = scrapy.Field()
    category = scrapy.Field()
    comments = scrapy.Field()
    str_id = scrapy.Field()
    # comment_size = scrapy.Field()

