import json
import scrapy
from bs4 import BeautifulSoup
from wynews.items import WynewsItem
import re
import time
import math

class wy_spider(scrapy.Spider):
    name = 'wyspider'
    # allowed_domains = ['news.163.com']
    # start_urls = ['https://news.163.com/']
    list_url = 'http://news.163.com/special/0001386F/rank_whole.html'

    def start_requests(self):
        yield scrapy.Request(url=self.list_url, callback=self.parse_list)

    # 解析新闻列表
    def parse_list(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        # print(response.txt)
        res = soup.select('.tabContents table tr')
        print(res)
        news_list = []
        for element in res:
            if element.select('a'):
                url = element.select('a')[0].get('href')
                title = element.select('a')[0].text
                clicks = None
                if element.select('.cBlue'):
                    clicks = element.select('.cBlue')[0].text
                one_news = {
                    'url': url,
                    'title': title,
                    'clicks': clicks
                }
                news_list.append(one_news)
                print(one_news)
        print(len(news_list))

        for one_news in news_list:
            yield scrapy.Request(url=one_news['url'], meta={'one_news': one_news}, callback=self.parse_one_news)

    # 解析每篇新闻内容
    def parse_one_news(self, response):
        html = response.text
        this_news = response.meta['one_news']
        item = WynewsItem()
        soup = BeautifulSoup(html, 'html.parser')
        item['url'] = this_news['url']
        item['clicks_num'] = this_news['clicks']
        item['title'] = soup.select('#epContentLeft h1')[0].text
        item['source'] = soup.select('#epContentLeft #ne_article_source')[0].text
        item['content'] = soup.select('#endText')[0].text
        time_block = soup.select('#epContentLeft .post_time_source')[0]
        item['time'] = re.findall('.*?(\d+.*)　来源', str(time_block), re.S)[0]
        spider_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item['spider_time'] = spider_time

        item['str_id'] = re.findall('^https?://.*?/19/[0-9]{4}/[0-9]{2}/(.*)?.html', str(item['url']), re.S)[0]
        cmt_url = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'+item['str_id']+'/comments/newList?ibc=newspc&limit=30&showLevelThreshold=72&headLimit=1&tailLimit=2&offset='
        yield scrapy.Request(url=cmt_url+'0', meta={'cmt_url': cmt_url, 'item':item}, callback=self.parse_first_page_comment)

    # 从第一页评论获取页数
    def parse_first_page_comment(self, response):
        results = response.text
        cmt_url = response.meta['cmt_url']
        item = response.meta['item']
        json_result = json.loads(results)
        total_page = math.ceil(json_result['newListSize']/30)
        # item['comment_size'] = json_result['newListSize']
        # print("total_page", total_page)
        # all_comments = {}
        item['comments'] = {}
        for k, v in json_result['comments'].items():
            # print(k)
            tmp_dic = {
                'cmt_id': v.get('commentId'),
                'cmt_content': v.get('content'),
                'cmt_vote': v.get('vote'),
                'cmt_against': v.get('against'),
                'cmt_create_time': v.get('createTime'),
                'cmt_anonymous': v.get('anonymous'),
                'user': {
                    'avatar': v.get('user').get('avatar'),
                    'location': v.get('user').get('location'),
                    'nickname': v.get('user').get('nickname'),
                    'userId': v.get('user').get('userId')
                }
            }
            item['comments'][k] = tmp_dic
        # for i in range(total_page):
        if total_page > 1:
            yield scrapy.Request(url=cmt_url+'30', meta={'item': item, 'index': 1, 'total_page': total_page, 'cmt_url': cmt_url}, callback=self.parse_comment)
        else:
            yield item
        # item['comments'] = all_comments
        # yield item


    # 解析每页的评论内容
    def parse_comment(self, response):
        print("parse_comment...")
        results = response.text
        json_result = json.loads(results)
        # all_comments = response.meta['all_comments']
        item = response.meta['item']
        # item['comments'] = json_result['comments']
        for k, v in json_result['comments'].items():
            # print(k)
            tmp_dic = {
                'cmt_id': v.get('commentId'),
                'cmt_content': v.get('content'),
                'cmt_vote': v.get('vote'),
                'cmt_against': v.get('against'),
                'cmt_create_time': v.get('createTime'),
                'cmt_anonymous': v.get('anonymous'),
                'user': {
                    'avatar': v.get('user').get('avatar'),
                    'location': v.get('user').get('location'),
                    'nickname': v.get('user').get('nickname'),
                    'userId': v.get('user').get('userId')
                }
            }
            item['comments'][k] = tmp_dic

        index = response.meta['index']
        total_page = response.meta['total_page']
        cmt_url = response.meta['cmt_url']
        if index == (total_page - 1):
            print("return item")
            yield item
        else:
            index = index+1
            yield scrapy.Request(url=cmt_url+str(index*30), meta={'item': item, 'index': index, 'total_page': total_page, 'cmt_url': cmt_url}, callback=self.parse_comment)
        # yield item

