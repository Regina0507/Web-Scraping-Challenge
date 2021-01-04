#!/usr/bin/env python
# coding: utf-8

# In[1]:


# !pip install bs4 --user


# In[2]:


# Import dependencies
import pandas as pd
import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


# In[3]:


# Configure ChromeDriver
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path)


# # NASA Mars News

# In[4]:


def mars_news():
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    article_container = news_soup.find('ul', class_='item_list')

    headline_date = article_container.find('div', class_='list_date').text
    news_title = article_container.find('div', class_='content_title').find('a').text
    news_p = article_container.find('div', class_='article_teaser_body').text

    return news_title, news_p


# # JPL Mars Space Images - Featured Image
# 
# 
# 

# In[5]:


def featured_image():
    base_url = 'https://www.jpl.nasa.gov'

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    img_elem = img_soup.find('h1', 'media_feature_title').text.strip()
        
    img_elem = img_soup.find('article', class_='carousel_item')['style']
    img_rel_url = img_elem.replace("background-image: url('", '')
    img_rel_url = img_rel_url.replace("');", '')
    img_rel_url = f'https://www.jpl.nasa.gov{img_rel_url}'
    featured_image_url = img_rel_url
       
    return featured_image_url


# # Mars Facts

# In[6]:


def mars_facts():
    url = 'https://space-facts.com/mars/'
    browser.visit(url)

    mars_facts_df = pd.read_html(url)
    mars_facts_df = mars_facts_df[0]
    mars_facts_df.columns = ['Description', 'Mars']
    mars_facts_df

    mars_facts_html = mars_facts_df.to_html(classes='table table-striped')
    
    return mars_facts_html


# In[7]:


# if you wanted to pull the HTML table directly from the page
# w/o Pandas, then you can. The HTML would, however, contain
# the formatting from the original web developer

html = browser.html
facts_soup = BeautifulSoup(html, 'html.parser')
facts_soup.find(id='tablepress-p-mars')


# # Mars Hemispheres
# 
# 

# In[8]:


def mars_hemispheres():

    # Initiate empty list of dictionaries (no dictionaries yet present)
    global hemisphere_image_urls
    hemisphere_image_urls = []
    
    # URL of page to be scraped and Configure Splinter
    # URL = universal resource locator (FYI)
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Capture HTML from URL
    html = browser.html

    # Get list of hemispheres 
    links = browser.find_by_css("a.product-item h3")

    # Traverse Splinter links
    for i in range(len(links)):

        #Find the elements on each loop 
        browser.find_by_css("a.product-item h3")[i].click()

        # Capture HTML from second URL (linked page)
        html = browser.html

        # Parse HTML from second URL (linked page) with BeautifulSoup
        mars_hemispheres_image_soup = BeautifulSoup(html, 'html.parser')

        # Use BeautifulSoup to zero in on image_title
        mars_hemispheres_image_title = mars_hemispheres_image_soup.find('h2', class_='title').text

        # Use BeautifulSoup to zero in on relative URL for wide_image (full image)
        mars_hemispheres_image_url = mars_hemispheres_image_soup.find('img', class_='wide-image')['src']

        # Augment relative URL to create full URL for wide_image (full image)
        mars_hemispheres_image_url = 'https://astrogeology.usgs.gov' + mars_hemispheres_image_url

        # Initiate empty dictionary
        hemisphere_dict = {}

        # Populate dictionary with results
        hemisphere_dict = {"title": mars_hemispheres_image_title, "img_url": mars_hemispheres_image_url}

        # Append dictionary to list of dictionaries
        hemisphere_image_urls.append(hemisphere_dict)

        # Use Splinter to go back to prior web page
        browser.back()
        
    return hemisphere_image_urls

mars_hemispheres()


# # Insert into Mongo DB

# In[9]:


def scrape_all():

    # Populate variables from the functions
    news_title, news_p = mars_news()
    featured_img_url = featured_image()
    mars_facts_html = mars_facts()

    # Assemble the document to insert into the database
    nasa_document = {
        'news_title': news_title,
        'news_paragraph': news_p,
        'featured_img_url': featured_img_url,
        'mars_facts_html': mars_facts_html
    }

    return nasa_document


# In[10]:


# Connect to MongoDB
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Connect to mars_app database
db = client.mars_app

# Connect to mars collection
mars = db.mars

# Gather document to insert
data_document = scrape_all()

# Insert into the mars collection
# mars.insert_one(data_document)

# Upsert into the mars collection (preferred to avoid duplicates)
mars.update_one({}, {'$set': data_document}, upsert=True)


# In[ ]:





# In[ ]:




