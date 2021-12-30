# Import Splinter, BeautifulSoup and Pandas dependecies
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment / Set up Splinter executable path
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_not_present_by_css('div.list_text', wait_time=1)

    # Set up the HTML parser.
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p



# ### JPL Space Images Featured Image

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# ### Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html" to scrape the facts table into a dataframe
        mars_facts_df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    mars_facts_df.columns=['Description', 'Mars', 'Earth']
    mars_facts_df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return mars_facts_df.to_html(classes="table table-striped")

# Hemispheres function

def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    links = browser.find_by_css('a.product-item img')

    # Iterate through all hemisphere links to extract image & title
    for i in range(len(links)):
        
        # Create dictionary to store image & title for each hemisphere
        hemispheres = {}
        
        # Find image & click link on website
        browser.find_by_css('a.product-item img')[i].click()
        
        # Find Sample image & extract image url
        sample_elem = browser.links.find_by_text('Sample').first
        hemispheres['img_url'] = sample_elem['href']
        
        # Find & extract image title
        hemispheres['title'] = browser.find_by_css('h2.title').text
        
        # Append list to dictionary
        hemisphere_image_urls.append(hemispheres)
        
        # Navigate back to home page
        browser.back()

    # 5. Quit the browser
    browser.quit()

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
