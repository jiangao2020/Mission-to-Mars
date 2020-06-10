# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser('chrome', 'chromedriver.exe', headless=True)
    # use our mars_news function to pull this data
    news_title, news_paragraph = mars_news(browser)
    hemisphere = hemisphere_image(browser)

    data = {"news_title": news_title, 
            "news_paragraph": news_paragraph, 
            "featured_image": featured_image(browser), 
            "facts": mars_fact(), 
            "last_modified": dt.datetime.now(),
            "cerberus_image": hemisphere[0].get('img_url'),
            "cerberus_title": hemisphere[0].get('title'),
            "schiaparelli_image": hemisphere[1].get('img_url'),
            "schiaparelli_title": hemisphere[1].get('title'),
            "syrtis_major_image": hemisphere[2].get('img_url'),
            "syrtis_major_title": hemisphere[2].get('title'),
            "valles_marineris_image": hemisphere[3].get('img_url'),
            "valles_marineris_title": hemisphere[3].get('title'),
            }
    return data

# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', 'chromedriver.exe', headless= False)

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object 
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try: 
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p 

### Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try: 
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url

def mars_fact():
    # Add try/except for error handling
    try:
        #use 'read_html' to scrape the facttable into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemisphere_image(browser):
    # Create a list of hemispheres
    hemimagelist = ['Cerberus Hemisphere Enhanced','Schiaparelli Hemisphere Enhanced','Syrtis Major Hemisphere Enhanced','Valles Marineris Hemisphere Enhanced']
    hemimage = []

    for product in hemimagelist:
        # Visit URL
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)

        full_image_elem = browser.find_by_text(product, wait_time=1)
        full_image_elem.click()
        

        # Parse the resulting html with soup
        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        try:
            img_url_rel = img_soup.select_one('img.wide-image').get("src")

        except AttributeError:
            return None

        # Use the base URL to create an absolute URL
        hemi = f'https://astrogeology.usgs.gov{img_url_rel}'

        # HTML parser
        html = browser.html
        news_soup = BeautifulSoup(html, 'html.parser')

        # Look for <h2> tag with class title
        hemititle = news_soup.select_one('h2.title').text

        # Create dictionary to store Cerberus info
        hemidictionary = {'img_url': hemi, 'title': hemititle}

        # Append dictionary to hemiList
        hemimage.append(hemidictionary.copy())

    return hemimage

browser.quit()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
