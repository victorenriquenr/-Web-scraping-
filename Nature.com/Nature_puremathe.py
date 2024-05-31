# Scraping Nature articles
#
# Author Víctor Núñez
# Date: 25-04-2024
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Libraries
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# The Magic
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


start = time.time()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

class Content:
    def __init__(self, title, abstract, doi, citations, accesses, online_attention, published_datetime,
                tweeters, blogs, facebook_pages, news_outlets, redditors, video_uploaders, wikipedia_page, 
                mendeley):
        self.title = title
        self.abstract = abstract
        self.doi = doi
        self.citations = citations
        self.accesses = accesses
        self.online_attention = online_attention
        self.published_datetime = published_datetime
        self.tweeters = tweeters
        self.blogs = blogs
        self.facebook_pages = facebook_pages
        self.news_outlets = news_outlets
        self.redditors =  redditors
        self.video_uploaders = video_uploaders
        self.wikipedia_page = wikipedia_page
        self.mendeley =  mendeley

    'tweeters', 'blogs', 'Facebook pages', 'news outlets', 
    'Redditors', 'Video uploaders', 'Wikipedia page', 'Mendeley'

    def to_dataframe(self):
        
        df = {'title': self.title,
              'abstract': self.abstract,
              'doi': self.doi,
              'citations' : self.citations,
              'accesses' : self.accesses,
              'online_attention' : self.online_attention,
              'published_datetime': self.published_datetime,
              'tweeters': self.tweeters,
              'blogs': self.blogs,
              'facebook_pages': self.facebook_pages,
              'news_outlets': self.news_outlets,
              'redditors': self.redditors,
              'video_uploaders': self.video_uploaders,
              'wikipedia_page': self.wikipedia_page,
              'mendeley': self.mendeley
             }
        return pd.DataFrame(df)



def getSoup(url):
    req =  requests.get(url, headers =  headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    #time.sleep(1)
    return soup

def InternalLinks(url):
    soup =  getSoup(url)
    InternalLinks = ['https://www.nature.com'+ x.get('href') for x in soup.find_all('a', href = re.compile('/articles/'))]
    return InternalLinks

def Scrape(numPage): 
    title = []; abstract = []; doi = [] ; citations = []; accesses= []
    online_attention = []; published_datetime = [] 
    tweeters = []; blogs = [] ;facebook_pages = [] ;news_outlets = []
    redditors = []; video_uploaders = [] ;wikipedia_page = []
    mendeley = []
    count = 1
    for page in range(1, numPage+1):
        URL = 'https://www.nature.com/search?subject=pure-mathematics&article_type=protocols%2Cresearch%2Creviews&page=2'+str(count)
        links = InternalLinks(URL)
        for element in links:
            soup = getSoup(element) 
            title.append(soup.find('h1').get_text())
            abstract.append(soup.find('meta', attrs={"name": "description"})["content"])
            doi.append('https://doi.org/'+soup.find('meta', attrs={"name": "citation_doi"})["content"])
            
            published_datetime.append(soup.find('time').get_text())
            
            try:
            	metrics_details = soup.find('div', class_="c-article-metrics-bar__wrapper u-clear-both").get_text().split()
            except:
                metrics_details = []

            if 'Citations' in metrics_details:
                i = metrics_details.index('Citations')
                citations.append(metrics_details[i-1])
            else:
                citations.append(0)
            
            if 'Accesses' in metrics_details:
                i = metrics_details.index('Accesses')
                accesses.append(metrics_details[i-1])
            else: 
                accesses.append(0)
            
            if 'Altmetric' in metrics_details:
                i = metrics_details.index('Altmetric')
                online_attention.append(metrics_details[i-1])
            else: 
                online_attention.append(0)

            #online attention, details:
            soup_metric =  getSoup(element+'/metrics')
            try:
                attention_string = soup_metric.find('div', class_= 'c-article-metrics__legend').get_text()
                elements = r'(\d+)\s+(tweeters|blogs|Facebook\s+pages|news\s+outlets|Redditors|Video\s+uploaders|Wikipedia\s+page|Mendeley)'
                
                a = re.findall(elements, attention_string)
                b = [item[0]+','+ item[1] for item in a]
                metrics = []
                
                for element in b:
                    x = element.split(",")
                    metrics.extend(x)
                
                if 'tweeters' in metrics:
                    i = metrics.index('tweeters')
                    tweeters.append(metrics[i-1])
                else:
                    tweeters.append(0)
                
                if 'blogs' in metrics:
                    i = metrics.index('blogs')
                    blogs.append(metrics[i-1])
                else:
                    blogs.append(0)
                
                if 'Facebook pages' in metrics:
                    i = metrics.index('Facebook pages')
                    facebook_pages.append(metrics[i-1])
                else:
                    facebook_pages.append(0)
                
                if 'news outlets' in metrics:
                    i = metrics.index('news outlets')
                    news_outlets.append(metrics[i-1])
                else:
                    news_outlets.append(0)
                
                if 'Redditors' in metrics:
                    i = metrics.index('Redditors')
                    redditors.append(metrics[i-1])
                else:
                    redditors.append(0)
                
                if 'Video uploaders' in metrics:
                    i = metrics.index('Video uploaders')
                    video_uploaders.append(metrics[i-1])
                else:
                    video_uploaders.append(0)
                
                if 'Wikipedia page' in metrics:
                    i = metrics.index('Wikipedia page')
                    wikipedia_page.append(metrics[i-1])
                else:
                    wikipedia_page.append(0)
                
                if 'Mendeley' in metrics:
                    i = metrics.index('Mendeley')
                    mendeley.append(metrics[i-1])
                else:
                    mendeley.append(0)
            except:
                tweeters.append(0)
                blogs.append(0)
                facebook_pages.append(0)
                news_outlets.append(0)
                redditors.append(0)
                video_uploaders.append(0)
                wikipedia_page.append(0)
                mendeley.append(0)
            
        count += 1    
    return Content(title, abstract, doi, citations, accesses, online_attention, published_datetime,
                  tweeters, blogs, facebook_pages, news_outlets, redditors, video_uploaders, wikipedia_page,
                  mendeley)
    

content = Scrape(2)
df = content.to_dataframe()

df['Topic'] = 'Pure-Mathematics'
print('Extraction complete')
df.to_csv('./dataset_phys.csv', index = False, header = True)

end = time.time()
total_time = end - start
print("Total time: {:.2f} seconds".format(total_time))
