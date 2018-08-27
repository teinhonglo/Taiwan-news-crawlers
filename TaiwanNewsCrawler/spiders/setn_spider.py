#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
三立新聞
the crawl deal with setn's news
Usage: scrapy crawl setn -o <filename.json> -s DOWNLOAD_DELAY=0.1
"""
import re
from datetime import date
from datetime import timedelta
import scrapy

YESTERDAY = (date.today() - timedelta(1)).strftime('%m/%d/%Y')


class SetnSpider(scrapy.Spider):
    name = "setn"

    def __init__(self, category=None, *args, **kwargs):
        super(SetnSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://www.setn.com/ViewAll.aspx?date={}&p=1'.format(YESTERDAY)
        ]
        self.last_page_flag = 0

    def parse(self, response):

        for news in response.css('.box ul li'):
            category = news.css('.tab_list_type span::text').extract_first()
            meta = {'category': category}
            url = news.css('a::attr(href)').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_news, meta=meta)

        last_two_pages = response.css('.pager a::attr(href)').extract()[-2:]
        page1 = last_two_pages[0].split('&p=')[1]
        page2 = last_two_pages[1].split('&p=')[1]

        if page1 == page2:
            self.last_page_flag = self.last_page_flag + 1

        if self.last_page_flag < 2:
            url_arr = response.url.split('&p=')
            current_page = int(url_arr[1])
            next_page_url = '&p='.join(
                url_arr[:-1]) + '&p=' + str(current_page + 1)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_news(self, response):
        title = response.css('.title h1::text').extract_first()
        content = ''
        date_of_news = ''
        if response.url.split('/')[3] == 'E':
            date_of_news = response.css('.time::text').extract_first()[:10]
            content = response.css('.Content2 p::text').extract()
        else:
            date_of_news = response.css('.date::text').extract_first()[:10]
            content = response.css('#Content1 p::text').extract()

        content = ''.join(content)

        yield {
            'website': "三立新聞",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': response.meta['category']
        }
