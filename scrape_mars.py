# %%
# Import dependencies

import pandas as pd
import pymongo
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
# %%
# Configure ChromeDriver
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path)

# %%
# # Insert into Mongo DB

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

    # consider closing browser here
    browser.quit()

    return nasa_document

# %%
# # NASA Mars News

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
# %%
# # JPL Mars Space Images - Featured Image

def featured_image():
    base_url = 'https://www.jpl.nasa.gov'

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Method 1: parsing through the style attribute in the article tag
    try:
        img_elem = img_soup.find('article', class_='carousel_item')['style']
        img_rel_url = img_elem.replace("background-image: url('", '')
        img_rel_url = img_rel_url.replace("');", '')
        #print(img_rel_url)
    except Exception as e:
        print(e)

    # Method 2: clicking the FULL TEXT button and pulling the image
    try:
        full_image_elem = browser.find_by_id('full_image')[0]
        full_image_elem.click()

        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        img_rel_url = img_soup.find('img', class_='fancybox-image')['src']
        #print(img_rel_url)
    except Exception as e:
        print(e)

    featured_image_url  = f'{base_url}{img_rel_url}'
    print(featured_image_url)
    
    return featured_image_url


# %%
# # Mars Facts

def mars_facts():
    url = 'https://space-facts.com/mars/'
    browser.visit(url)

    mars_facts_df = pd.read_html(url)
    mars_facts_df = mars_facts_df[0]
    mars_facts_df.columns = ['Description', 'Mars']
    mars_facts_df

    mars_facts_html = mars_facts_df.to_html(classes='table table-striped', index=False, border=0)
    
    return mars_facts_html
# %%
# # Mars Hemispheres


# %%
# Run Script

# if __name__ == '__main__':
#    scrape_all()