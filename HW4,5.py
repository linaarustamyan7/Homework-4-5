#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import pandas as pd
import scrapy
import quandl
import re
import os
from urllib.parse import urlparse
from urllib.parse import urljoin
import numpy as np
from datetime import datetime
import time
import datetime
from datetime import date
from tqdm import tqdm
from matplotlib import pyplot as plt
import googlemaps
from scrapy.crawler import CrawlerProcess


# # 4) GoogleMaps

# In[1]:


get_ipython().system('pip install requests')


# In[2]:


get_ipython().system('pip install googlemaps')


# In[5]:


get_ipython().system('pip install quandl')


# In[ ]:


get_ipython().system('pip install scrapy')


# In[4]:




API_KEY = "AIzaSyAumnnMv0HnNmaGPelM1lSabQPuaL0Oc8w"
regions = ['Երևան','Աշտարակ','Արտաշատ','Արմավիր','Գավառ','Գյումրի','Եղեգնաձոր','Իջևան','Կապան','Հրազդան','Վանաձոր']
pairs = [[regions[p1],regions[p2]] for p1 in range(len(regions)) for p2 in range(p1+1, len(regions))]
def get_distance(start, end, API_KEY):
    page = requests.get(f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={start}&destinations={end}&key={API_KEY}")
    response = page.json()
    print(f'The distance between {start} and {end} is {response["rows"][0]["elements"][0]["distance"]["text"]}')
for i in pairs:
    get_distance(i[0],i[1],API_KEY)


# # 2) Quandl for Tesla

# In[8]:


data = quandl.get("WIKI/TSLA", start_date="2017-01-01", end_date = "2019-01-01")
open_return = data['Open'].pct_change()
average_open_return = open_return.mean()

range = data['High'] - data['Low']
range_percent_change = range.pct_change()
median_range_perc_change = range_percent_change.median()

output = {"Average daily percentage change of the opening price":average_open_return,"Median daily percentage change of range between highest and lowest daily prices":median_range_perc_change}
output


# # 5) Menu.am

# In[18]:


get_ipython().system('pip install scrapy')


# In[3]:


class MenuScraper(scrapy.Spider):
    name = "Menu_am"
    start_urls = ["https://www.menu.am/?status=all&sort=default"]
    custom_settings = {
       
        "FEED_FORMAT": "json",
        "FEED_URI": "menu_am.json"
        
    }
    def parse(self, response):

        
        titles = response.css("div[class='fl list-title']>a::attr(title)").extract()
        categories = response.css("span[class='restType']::text").extract()
        open_hours = response.css("span[class='new_list_time_block_inner']::text").extract()
        urls = ["https://www.menu.am" + i for i in response.css("div[class='fl list-title']>a::attr(href)").extract()]
        blocks = response.xpath("//div[contains(@class, 'item ')]")
        ratings = []
        rating_ = []
        for i in blocks:
            rating_.append(i.css('div[class="new_favorites_and_rates_block"]::text').extract())
        for j in rating_:
            if(j == []):
                ratings.append(0)
                continue
            ratings.append(j[0].strip())
        for title, category, open_time, hyperlink, rating in zip(titles, categories, open_hours, urls, ratings):
            yield {
                "Title": title,
                "Rating": rating,
                "Category": category,
                "Open Hours": open_time,
                "Hyperlink": hyperlink
            }


# In[4]:


process = CrawlerProcess()
process.crawl(MenuScraper)
process.start()


# In[5]:


Data = pd.read_json("menu_am.json")
Data


# In[6]:


sort_rating = Data.sort_values(by = "Rating", ascending = False)
Times = Data['Open Hours']
hours = []
for i in Times:
    if(i[8:10] != ''):
        if(int(i[8:10])<=19 and int(i[8:10])>12):
            hours.append(i)


# In[7]:


#Restaurants which close exactly at or sooner than 7pm
b = Data['Title'].loc[Data['Open Hours'].isin(hours)]
#Top rated category 
c= str(sort_rating.iloc[0]['Category'])
results = b,c
results


# # 3) Dbnomics

# In[11]:


url= "https://api.db.nomics.world/v22/series/IMF/DOT/A.AM.TMG_CIF_USD.W00?observations=1"


# In[12]:


response = requests.get(url)


# In[13]:


arm_import = pd.read_json(response.text)


# In[14]:


year_import = pd.DataFrame({
    'year': arm_import.series.docs[0]["period"],
    'value': arm_import.series.docs[0]["value"]
})


# In[15]:


year_import[year_import["value"] == np.max(year_import["value"])]["year"].values[0]


# In[16]:


url_contries_codes = "https://www.iban.com/country-codes"
df_codes = pd.read_html(url_contries_codes)


# In[17]:


countries_codes = df_codes[0]["Alpha-2 code"]


# In[18]:


latest_income = {}

for country_code in tqdm(countries_codes):
  response = requests.get(f"https://api.db.nomics.world/v22/series/IMF/DOT/A.AM.TMG_CIF_USD.{country_code}?observations=1")
  df_temp = pd.read_json(response.text)

  print("\n\n\\n\n")
  print(country_code)
  print(df_temp.columns)
  if "series" in df_temp.columns:
    latest_income[country_code] = df_temp["series"].docs[0]['value'][-1]


# In[19]:


third_partner_value = sorted(latest_income.values(), reverse=True)[2]


# In[20]:


third_partner_code = list(latest_income.keys())[list(latest_income.values()).index(third_partner_value)]


# In[23]:


third_partner_country = df_codes[0][df_codes[0]["Alpha-2 code"] == third_partner_code]["Country"].values[0]
third_partner_country


# In[24]:


url_arm_georgia = "https://api.db.nomics.world/v22/series/IMF/DOT/A.AM.TMG_CIF_USD.GE?observations=1"


# In[25]:


response = requests.get(url_arm_georgia)
df_georgia = pd.read_json(response.text)


# In[26]:


df_georgia_year_import = pd.DataFrame({
    'year': df_georgia.series.docs[0]["period"],
    'value': df_georgia.series.docs[0]["value"]
})


# In[27]:


plt.plot(df_georgia_year_import['year'], df_georgia_year_import['value'])
# overal tendence used to grow, but in the past 2 years it dropped a little bit


# In[ ]:




