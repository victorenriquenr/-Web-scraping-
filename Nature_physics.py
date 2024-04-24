# Scraping Nature_Physics
#
# Author: Víctor Núñez
# Date: 24-04-2024
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



# Libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
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
    def __init__(self, title, abstract, doi, citations, accesses, online_attention, published_datetime):
        self.title = title
        self.abstract = abstract
        self.doi = doi
        self.citations = citations
        self.accesses = accesses
        self.online_attention = online_attention
        self.published_datetime = published_datetime

    def to_dataframe(self):
        
        df = {'title': self.title,
              'abstract': self.abstract,
              'doi': self.doi,
              'citations' : self.citations,
              'accesses' : self.accesses,
              'online_attention' : self.online_attention,
              'published_datetime': self.published_datetime
             }
        return pd.DataFrame(df)



def getSoup(url):
    req =  requests.get(url, headers =  headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    time.sleep(1)
    return soup

def InternalLinks(url):
    soup =  getSoup(url)
    InternalLinks = ['https://www.nature.com'+ x.get('href') for x in soup.find_all('a', href = re.compile('/articles/'))]
    return InternalLinks

def Scrape(numPage): 
    title = []; abstract = []; doi = [] ; citations = []; accesses= []
    online_attention = []; published_datetime = []
    count = 1

    for page in range(1, numPage+1):
        URL = 'https://www.nature.com/nphys/research-articles?searchType=journalSearch&sort=PubDate&page='+str(count)
        links = InternalLinks(URL)
        for element in links:
            soup = getSoup(element) 
            title.append(soup.find('h1').get_text())
            abstract.append(soup.find('meta', attrs={"name": "description"})["content"])
            doi.append('https://doi.org/'+soup.find('meta', attrs={"name": "citation_doi"})["content"])
            published_datetime.append(soup.find('time').get_text())
            
            metrics_details = soup.find('div', class_="c-article-metrics-bar__wrapper u-clear-both").get_text().split()
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
        count += 1
    
            
    return Content(title, abstract, doi, citations, accesses, online_attention, published_datetime)
    

content = Scrape(1) # Choose the number of pages to scrape.
df = content.to_dataframe()
print('Extraction complete')

df['Topic'] = 'Physics'
df.to_csv('./dataset_phys.csv', index =  False, header =  True)


end = time.time()
total_time = end - start
print("Total time: {:.2f} seconds".format(total_time))
