#! Scrape a Nature
#!
#! Objetivos: Extraer data de artículos en Nature.com
#!
#! Víctor Núñez
#!---------------------------------------------------------------------


import requests
from bs4 import BeautifulSoup 
from scrapy.item import Field, Item
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from lxml import html
import re 



#----------------------------------------------------------------------

class Nature_Articles(Item):
    journal_id = Field()
    source = Field()
    title = Field()
    doi = Field()
    subject_1 = Field()
    subject_2 = Field()
    publicationDate = Field()
    numberPages = Field()
    altmetric_score = Field()
    #tweeters = Field()

class NatureSpider(CrawlSpider):
    name = 'natureSpider'
    custom_settings = { 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                       'CLOSESPIDER_PAGECOUNT': 10000,
                       'FEEDS': {'NatureArticles.csv': {'format': 'csv'}}
    }
    
    allowed_domains = ['nature.com']
    start_urls = ['https://www.nature.com/nature/research-articles']
    download_delay = 2
    
    rules = [Rule(LinkExtractor(allow = re.compile('^(.*)(/articles/)(?!.*figures)(?!.*tables)(.*)$')),
                  follow=True,
                  callback='parse_nature')]
    
    def parse_nature(self,response):
        bs = BeautifulSoup(response.text, 'html.parser')
        item = Nature_Articles()
        
        try:  
            item['journal_id'] = bs.find('meta', {'name':'journal_id'}).get('content')
            item['source']  = bs.find('meta',{'name':'dc.source'}).get('content')
            item['title']   = bs.find('meta', {'name':'dc.title'}).get('content')
            item['doi']     = bs.find('meta', {'name':'DOI'}).get('content')
            item['subject_1'] = bs.find_all('meta', {'name':'dc.subject'})[0].get('content')
            item['subject_2'] = bs.find_all('meta', {'name':'dc.subject'})[1].get('content')
            item['publicationDate'] = bs.find('meta', {'name':'prism.publicationDate'}).get('content')
            startingPag = int(bs.find('meta', {'name':'prism.startingPage'}).get('content'))
            endingPage  = int(bs.find('meta', {'name':'prism.endingPage'}).get('content'))
            item['numberPages'] = endingPage-startingPag
            item['altmetric_score'] = bs.find('p',class_="c-article-metrics-bar__count").get_text().replace('Altmetric','').strip()
        except:
            None
        
        #Metrics
        #metric_url = 'https://www.nature.com'+bs.find_all('a', href = re.compile('^/articles(.*/metrics)$'))[0].get('href')
        #headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",}
        #req = requests.get(metric_url, headers = headers)
        #req.encoding= 'utf-8'
        #parser_metric = html.fromstring(req.content)
        
        #item['altmetric_score']= parser_metric.xpath('//div[@class="c-article-metrics__image"]/img/@alt')[0].replace('Altmetric score', '')
        #item['tweeters'] = parser_metric.xpath('//div[@class="c-article-metrics__legend"]/ul/li/span/text()')[0].replace('tweeters','')
        
        return item
  

#Start
process = CrawlerProcess()
process.crawl(NatureSpider)
process.start()