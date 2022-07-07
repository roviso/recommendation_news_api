from time import sleep
import traceback
from datetime import timedelta
from celery import current_task
from celery import states
from celery.exceptions import Ignore
# from celery import periodic_task
import logging
from worker import celery
from threading import Thread

import time, os, re
from bs4 import BeautifulSoup
import requests
from dateutil.parser import parse
from datetime import datetime
from urllib.parse import urlparse
from requests.exceptions import RequestException
from database import async_session

from pydantic import BaseModel
from typing import Optional
from typing import List
from schemas import  author_schema
# article_schema,

from routers.source import getAllSource
from routers.latest import create_latest_article, get_article_by_url
from routers.author import create_author
from routers import clicks ## clicks had to be imported for some reason unknown
from routers.keywords import update_articles_keywords



CONNECTION_TIMEOUT = 10
DEFAULT_IMAGE = '/media/system/prixa_image.png'
image_error = {}
scraped_news = {}


logger = logging.getLogger(__name__)


class CreateLatestArticle(BaseModel):
    # author : author_schema.Author
    url: str
    head_image : Optional[str]
    heading : Optional[str]
    date : Optional[str]

    label: Optional[str]

    content : List[Optional[str]]
    additional_img : List[Optional[str]] = None
    source : Optional[str]
    likes: Optional[int] = 0
    shares: Optional[int] = 0


    views: Optional[int] = 0
    ignores: Optional[int] = 0
    total_comments: Optional[int] = 0
    bookmarks: Optional[int] = 0
    author_id: str
    type : str
    class Config:
        orm_mode = True
# @periodic_task(
#     run_every=(timedelta(minutes=0.1)),
#     name="run_similar",
#     ignore_result=True
# )

def run_similar():
	"""
	Executed similarity task periodically
	"""
	print('---------------------------')
	print('Executing news similarity')
	try:
		execute_similar('a','b')
	except Exception as e:
		print("Error while executing similarity.")
		print(str(type(e)) + ' : ' + str(e))
	print('News similarity complete')
	print('---------------------------')

# @celery.task
def execute_similar(x,y):
    print(f"__________{x}__________EXECUTING SIMILAT>>> GWAIII >>>> GWAIIII ____________{y}______________")


@celery.task(name='hello.task', bind=True)
def hello_world(self, name):
    try:
        if name == 'error':
            k = 1 / 0
        for i in range(60):
            sleep(1)
            self.update_state(state='PROGRESS', meta={'done': i, 'total': 60})
        return {"result": "hello {}".format(str(name))}
    except Exception as ex:
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(ex).__name__,
                'exc_message': traceback.format_exc().split('\n')
            })
        raise 


@celery.task
async def refresh_sources():
    print('refreshing the source')
    sources = await getAllSource()
    """
	Refreshing all sources for scraping
	"""
    logger.debug('---------------------------')
    logger.debug('Refreshing all sources')
    threads = []
    if len(sources) == 0:
        return {'error' : 'No Source Found'}

    for source in sources:
        print(f"Using RSS LINK: {source.link} from source: {source.name}")
    try:
        for source in sources:
            if source.link_type == 'instant_rss':
                # t = Thread(target=scrape_instant_rss, args=[source.pk, source.category_id, source.link, source.link_prefix])
                # threads.append(t)
                # t.start()
                print("____________INSTANT RSS FOUND__________________________")
        #scrape_instant_rss(source.pk, source.category_id, source.link, source.link_prefix)
            elif source.link_type == 'normal_rss':
                print("_________________STARTING NORMAL RSS SCRAPPING________________________")
                if source.default_image:
                    default_image = source.default_image.url
                else:
                    default_image = DEFAULT_IMAGE
                
                await scrape_normal_rss(source.id, source.name , source.link, source.link_prefix, source.selector, source.image_selector, source.author_selector ,source.exception_selector, default_image)
        #         t = Thread(target=scrape_normal_rss, args=[source.id, source.link, source.link_prefix, source.selector, source.image_selector, source.exception_selector, default_image])
        #         threads.append(t)

        #         t.start()
        # for t in threads:
        #     t.join()

        # print(t, threads,5555555555555555555555555555555)
        updated_articles = await update_articles_keywords()
        print("UPDATED ARTICLES ARE: ",updated_articles)

    except Exception as e:
        logger.debug("Error: unable to start thread")
        logger.debug(str(e))
        logger.debug('---------------------------\n')

@celery.task(name='scrape_normal_rss')
async def scrape_normal_rss(pk, name ,link, prefix, selector, image_selector, author_selector ,exception_selector, default_image, debug=False, debug_link=None):
    """
    Tasks for scraping normal rss
    Collect link from all items and scrape the particular link
    Debug=True for rss debuging
    """
    source = name
    print("* Scraping normal rss link : " + link)
    global image_error, scraped_news

    image_error[pk] = 0
    scraped_news[pk] = 0

    # checking if selector are empty
    if len(str(selector).strip()) < 1 or len(str(image_selector).strip()) < 1:
        print('Selector cannot be empty. '+link)
        if debug:	# Debugging mode
            return {'error': 'Selector cannot be empty'}
        return

    try:
        # sending request to the rss link
        r = requests.get(link, timeout=CONNECTION_TIMEOUT)
        soup = BeautifulSoup(r.text, "xml")

        if debug:	# Debugging mode
            soup_temp = BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print('Error connecting rss url. '+link)
        if debug:	# Debugging mode
            return {'error' : 'Error connecting url'}
        return

    # getting all items from rss feed
    items = soup.find_all('item')
    if len(items) == 0:
        print('No items available in rss feed. '+link)
        if debug:	# Debugging mode
            return {'error' : 'No items available in rss feed. Please check the rss link.', 'rss': str(soup_temp)}

    # looping all items

    for item in reversed(items):


        # published date (default current date)
        try:
            pubDate = item.find('pubDate').get_text()
            pubDate = parse(str(pubDate))

        except:
            if not debug:
                pubDate = datetime.now()
                # print(f"using pubDate {pubDate}")
            else:
                pubDate = ''

        # getting link from item
        link = item.find('link')
        if not link:
            # if the item has no link
            print('Unable to find link in rss item. '+link)
            if debug:	# Debugging mode
                return {'error' : 'Unable to find link in rss item.', 'rss': str(soup_temp)}
        link = link.text.strip()


        article = await get_article_by_url(link)

        if not article: 

            if debug:
                # sending output for debugging mode.
                if debug_link != None and debug_link != '':

                    link = debug_link
                output = scrape_news(pk, source, link, prefix, selector, image_selector, author_selector, exception_selector, default_image, pubDate, debug)
                output['rss'] = str(soup_temp)
                return output

            # scraping news link
            await scrape_news(pk, source, link, prefix, selector, image_selector,author_selector, exception_selector, default_image, pubDate, debug)

    
    

    # if there are no image available in every link, alerting debugger	( only if more than 3 news )
    if(scraped_news[pk] == image_error[pk] and scraped_news[pk] > 3):
        print('Unable locate images. Please debug this source. Make sure the image selector is correct. '+link)



async def scrape_news(pk, source, link, prefix, content_selector, image_selector, author_selector, exception_selector, default_image, pubDate, debug):
    """
    Scrapes and saves news from news link
    Content selector and image selector is strictly required
    """

    global image_error, scraped_news
    try:
        # link = "https://www.thahakhabar.com/news/78710"

        # Checking news if exists
        # print(checkNews(link, prefix))
        # if checkNews(link, prefix) and not debug:
        #     return

        print('Scraping news from link: '+link)

        # Requesting news link
        response = requests.get(link, timeout=CONNECTION_TIMEOUT)
        response.encoding = 'utf-8'
        link_soup = BeautifulSoup(response.text, 'html5lib')

        # getting title
        title_soup = link_soup.find("meta", {"property": "og:title"})
        # print(title_soup)
        if title_soup:
            title = str(title_soup['content'])
            # print('titke is : ', title)
        else:
            # if meta tag is not available
            title_soup  = link_soup.find("title")
            if title_soup:
                title = title_soup.text
            else:
                raise Exception('Unbale to locate title. '+link)
        del title_soup

        # extracting image
        image = default_image 	# using default image ( from argument )

        attribute = 'src'
        # getting custom attribute if exists
        if image_selector.find('|') >= 0:
            custom_selector = image_selector
            image_selector = custom_selector.split('|')[0]
            attribute = custom_selector.split('|')[1]
            del custom_selector


        # getting image link from content
        image_soup = link_soup.select(image_selector, limit=1)
        if len(image_soup) > 0:
            # image tag is available
            if image_soup[0].has_attr(attribute):
                image = str(image_soup[0][attribute]).strip()
                if checkImageUrl(image):
                    image = generate_absolute_url(link, image)
                    # print(f"image is {image}")
                else:
                    # image attribute is empty
                    image = default_image

        # alerting if there is no image in all link
        if pk in scraped_news:
            scraped_news[pk] += 1
            if image == default_image:
                image_error[pk] += 1
                #logger.warn('Unable to locate image. Saving default image. '+link)



        # authorselector = author_selector
        author = link_soup.select(author_selector, limit=1)
        
        author_img = author[0].find_all('img')
        author_img = author_img[0]['src'].strip()

        author_name = author[0].find_all('a')
        author_name = author_name[0].text.strip()

        new_author = author_schema.Author(
            author_name = author_name,
            author_img= author_img,
            source = source
        )

        created_author = await create_author(new_author)

        if not created_author:
            raise Exception(f'Could not add author')


        # extracting content
        content = link_soup.select(content_selector, limit=1)
        if len(content) < 1:
            raise Exception(f'Content not available or invalid content selector.')
        del link_soup

        # getting all content and removing exception from exception_selector
        content = content[0]

        addtional_img = [img['src'] for img in content.find_all('img')]
        addtional_img


        # for _selector in exception_selector.split(','):
        #     _selector = _selector.strip()
        #     if _selector != '':
        #         exception_soups = content.select(_selector)
        #         [exception_soup.extract() for exception_soup in exception_soups]

        # # Removing content images
        # images = content[0].find_all('img')
        # [image.extract() for image in images]

        # # Removing content videos
        # videos = content[0].find_all('iframe')
        # [video.extract() for video in videos]

        """
        -- Extract only p, ul, ol from content
        """

        # collecting all paragraphs as content
        paragraphs = content.find_all(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'])
        # paragraphs = content.findChildren(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'], recursive=False)

        content = [ '' if is_empty_soup(p) else str(p) for p in paragraphs]

        content = [i for i in content if i] ## removing empty paragraph
        # print(content)
        final_content = [''.join(content)]
        
        # content_list = []
        # for c in content:   
        #     new_content = html2text.html2text(c)
        #     content_list.append(new_content)  


        if len(content) < 1:
            raise Exception('Empty Content.')

        # Downloading and saving image
        if not debug:
            # image = saveImage(image)
            print(f"saving image {image}")

        # if not debug:
        #     # Calling Save Function
        #     # return saveNews(pk, category_id, link, title, image, content, pubDate)
        #     print("saving news with: ", pk, category_id, link, title, image, content, pubDate,"nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
        # else:
            # returning for debugging output
        article =  {
            # 'id': pk,
            'url': link,
            'heading': title,
            'head_image': image,
            'content': final_content,
            'date': str(pubDate),
            'additional_img': addtional_img,
            # 'label': 'test_label',
            'source': source,
            'like': 0,
            'shares': 0,
            'views': 0,
            'ignores': 0,
            'total_comments':0,
            'bookmarks':0,
            'type': 'latest',
            'author_id': created_author.id
        }

        new_article = CreateLatestArticle(**article)
        await create_latest_article(new_article)

    except RequestException as e:
        print('Request error. Unable to connect url : '+link)
        if debug:	# Debugging mode
            return {'error' : 'Request error. Unable to connect url.', 'link': link}

    except Exception as e:
        print(str(type(e)) + ' : ' + str(e) +" : "+link)
        if debug:	# Debugging mode
            return {'error' : str(type(e)) + ' : ' + str(e), 'link': link}




def checkImageUrl(image_url):
	""" 
	checks if image_url is valid or not 
	"""

	if(len(image_url) == 0):
		# image url is empty
		return False

	image_parsed = urlparse(image_url)
	if not image_parsed.path:
		# image_url doesn't contain any path
		return False
	return True

def checkNews(url, prefix):
	"""
	checking if news with url exists or not
	"""
	url = url.strip()
	if prefix:
		pattern = re.compile(prefix)
		if not pattern.match(url):
			return True
    
	# news = News.objects.filter(url=url)

	if len(url):
		return True
	return False



def generate_absolute_url(link, relative_link):
	"""
	generating absolute url from relative url
	
	Example:
	link: http://thakhabar.com/news/18998
	relative_link: /images/1039.jpg
	return: http://thakhabar.com//images/1039.jpg

	"""

	root_link = urlparse(link)[0]+'://'+urlparse(link)[1]
	if not bool(urlparse(relative_link).netloc) :
		if len(relative_link) < 1:
			return root_link
		if relative_link[0] == '/':
			return root_link+relative_link
		return root_link+'/'+relative_link
	return relative_link


def is_empty_soup(soup):
	return len(soup.contents) <= 0
	return len(soup.text.strip()) == 0



# scrape_news(pk = 1, 
#         category_id = 1, 
#         link = "https://www.thahakhabar.com/news/78710", 
#         prefix = None, 
#         selector = ".detail-news-details-paragh", 
#         image_selector="meta[property='og:image']|content", 
#         exception_selector = "", 
#         default_image = None, 
#         pubDate = None, 
#         debug = False)


# {
#     "domain": "farakdhar.com",
#     "author_selector": ".news-info",
#     "id": 1,
#     "link": "https://farakdhar.com/hamro-rss",
#     "default_image": "",
#     "created_at": null,
#     "link_prefix": "",
#     "analytics_id": "UA-125866437-1",
#     "updated_at": null,
#     "link_type": "normal_rss",
#     "category_id": 0,
#     "deleted_at": null,
#     "selector": "div.news-detail-content",
#     "pubDate": "",
#     "name": "farakdar",
#     "exception_selector": "string",
#     "debug": false,
#     "image": "sources/Snowberry_Dots.png",
#     "priority": 0,
#     "disable": false,
#     "image_selector": "meta[property='og:image']|content"
# }