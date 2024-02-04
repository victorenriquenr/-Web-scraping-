'''
==================================
'ScrapePopulation' by V.E Núñez
==================================
Objective: Population data extraction for the last years.

LAST EDITED: January 27 - 2024
'''


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

#Start with the url (The website is in Spanish):
url = 'https://datosmacro.expansion.com/demografia/poblacion'
years= [2019,2020,2021,2022,2023] 


#Define a function to extract data from the website
def getData(url):
    csvFile = open('WorldPopulation.csv','w+')
    writer = csv.writer(csvFile)
    writer.writerow(['Country','Date','Density', 'Population','Var'])

    for year in years:
        req = requests.get(url+'?anio='+str(year), headers = headers)
        bs  = BeautifulSoup(req.text, 'html.parser')
        
        #Find the table containing the data
        table = bs.find('table', id ='tb1').find('tbody')
        for element in table:
            #Extract country information
            country= element.find('a').get('title').split('-')[0]
            
            #Extract population, density, and variation data
            density,population,var = element.find_all('td', class_ = 'numero')
            density= density.text
            population = population.text
            var = var.text
            
            #Try to extract the date; use the current year if not available
            try:
                date = element.find('td', class_ = 'fecha').text
            except:
                date = str(year)
            writer.writerow([country,date,density,population,var])
        time.sleep(1)
    csvFile.close()

getData(url)

#Remove duplicate
data = pd.read_csv('WorldPopulation.csv')
data = data.drop_duplicates()
data.to_csv('WorldPopulation.csv', index = False)

# The name of the country is still in Spanish!