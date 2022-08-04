from time import sleep
import traceback
from nepali.datetime import nepalidatetime  
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

from models import source_model
from routers.source import getAllSource
from routers.label import get_label_by_name,addlabel

from routers.latest import create_latest_article, get_article_by_url
from routers.author import create_author, search_author
from routers import clicks ## clicks had to be imported for some reason unknown
from routers.keywords import update_articles_keywords


from crud import crud_scrap





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

    label_id: Optional[int]

    content : List[Optional[str]]
    additional_img : List[Optional[str]] = None
    source_id : Optional[int]
    likes: Optional[int] = 0
    shares: Optional[int] = 0


    views: Optional[int] = 0
    ignores: Optional[int] = 0
    total_comments: Optional[int] = 0
    bookmarks: Optional[int] = 0
    author_id: str
    type : str



# @periodic_task(
#     run_every=(timedelta(minutes=0.1)),
#     name="run_similar",
#     ignore_result=True
# )


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
    """
    Refreshes the Scource and starts scrapping fro the source RSS
    """
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
            
            # if not source.default_image:
            #     source.default_image = DEFAULT_IMAGE
            # else:
            #     default_image = DEFAULT_IMAGE
            # if source.id == 5:
            print(f"_________________STARTING NORMAL RSS SCRAPPING: {source.name}________________________")
            await scrape_normal_rss(source)
                # await scrape_normal_rss(source.id, source.name , source.link, source.link_prefix, source.selector, source.image_selector, source.author_selector ,source.exception_selector, default_image)
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
async def scrape_normal_rss(source: source_model.Source ):
    """
    Tasks for scraping normal rss
    Collect link from all items and scrape the particular link
    Debug=True for rss debuging
    """

    source_name = source.name
    print("* Scraping normal rss link : " + source.link)
    global image_error, scraped_news

    image_error[source.id] = 0
    scraped_news[source.id] = 0

    # checking if selector are empty
    if len(str(source.content_selector).strip()) < 1 or len(str(source.image_selector).strip()) < 1:
        print('Selector cannot be empty. '+source.link)
        # if source.debug:	# Debugging mode
        return {'error': 'Selector cannot be empty'}
        

    try:
        # sending request to the rss link
        r = requests.get(source.link, timeout=CONNECTION_TIMEOUT)
        soup = BeautifulSoup(r.text, "xml")

    except Exception as e:
        print('Error connecting rss url. '+source.link)

        return {'error' : 'Error connecting url'}


    # getting all items from rss feed
    items = soup.find_all('item')
    if len(items) == 0:
        print('No items available in rss feed. '+source.link)
    # looping all items

    for item in reversed(items):
        # published date (default current date)
        try:
            pubDate = item.find('pubDate').get_text()
            pubDate = nepalidatetime.from_datetime(parse(str(pubDate)))

        except:
            pubDate = nepalidatetime.now()

        try:
            # getting link from item
            link = item.find('link')
            if not link:
                # if the item has no link
                print('Unable to find link in rss item. '+link)

            link = link.text.strip()

            print(f"Scrapping from link: {link}")


            articleInDb = await get_article_by_url(link)
            """ Checking if the article is in database and ignoreing the scraping process if so."""

            if not articleInDb: 
                print(f"article not foind in database... continuing scrapping...")

                # scraping news link
                
                await scrape_news(source, link,pubDate )
        except:
            continue




async def scrape_news(source: source_model.Source, link: str, pubDate):
    """
    Scrapes and saves news from news link
    Content selector, image selector, label selector is strictly required
    """

    global image_error, scraped_news
    try:
        print('Scraping news from link: '+link)
        news_scrapper = crud_scrap.ScrapeLinkX(source,link)
        title = news_scrapper.scrape_title()
        head_image = news_scrapper.scrape_img(source.image_selector)
        author = news_scrapper.scrape_author(author_name_selector =source.author_name_selector,author_img_selector =source.author_img_selector)
        content, additional_img = news_scrapper.scrape_content(source.content_selector, None)
        label = news_scrapper.scrape_label(source.label_selector)


        author_exists = await search_author(author.author_name)
        """ Checking if the author exists in the db"""
        if not author_exists:
            print(f"Author: {author.author_name} not found in db... adding the author..")
            authorInDB = await create_author(author)
            """ Creating new author in DB"""
            if not authorInDB:
                raise Exception(f'Could not add author, PLEASE CHECK AUTHOR SELECTOR....')
        else:
            authorInDB = author_exists
            print(f"Author: {author_exists} found in DB...")
        author_id = authorInDB.id


        if not label:
            label = 'समाचार'

        labelInDb = await get_label_by_name(label)
        if not labelInDb:
            print("NO LABEL IN DB")
            labelInDb = await addlabel(label)
        

        article =  {
            # 'id': pk,
            'url': link,
            'heading': title,
            'head_image': head_image,
            'content': content,
            'date': str(pubDate),
            'additional_img': additional_img,
            'label_id': labelInDb.id,
            'source_id': source.id,
            'like': 0,
            'shares': 0,
            'views': 0,
            'ignores': 0,
            'total_comments':0,
            'bookmarks':0,
            'type': 'latest',
            'author_id': author_id
        }

        print(f"adding article {article} to the database ...")

        new_article = CreateLatestArticle(**article)
        article_created = await create_latest_article(new_article)
        if article_created:
            print("ARTICLE SUCCESFULLY ADDED")
        else:
            raise Exception(f'UNABLE TO ADD ARTICLE TO DB')

    except RequestException as e:
        print('Request error. Unable to connect url : '+link)
        # if source.debug:	# Debugging mode
        return {'error' : 'Request error. Unable to connect url.', 'link': link}

    except Exception as e:
        print(str(type(e)) + ' : ' + str(e) +" : "+link)
        # if source.debug:	# Debugging mode
        return {'error' : str(type(e)) + ' : ' + str(e), 'link': link}



# async def scrape_news(source: source_model.Source, link: str, pubDate):
#     """
#     Scrapes and saves news from news link
#     Content selector, image selector, label selector is strictly required
#     """

#     global image_error, scraped_news
#     try:
#         # link = "https://www.thahakhabar.com/news/78710"

#         # Checking news if exists
#         # print(checkNews(link, prefix))
#         # if checkNews(link, prefix) and not debug:
#         #     return

#         print('Scraping news from link: '+link)

#         # Requesting news link
#         response = requests.get(link, timeout=CONNECTION_TIMEOUT)
#         response.encoding = 'utf-8'
#         link_soup = BeautifulSoup(response.text, 'html5lib')

#         # getting title
#         title_soup = link_soup.find("meta", {"property": "og:title"})
#         # print(title_soup)
#         if title_soup:
#             title = str(title_soup['content'])
#             print('title: ', title)
#         else:
#             # if meta tag is not available
#             title_soup  = link_soup.find("title")
#             if title_soup:
#                 title = title_soup.text
#                 print('title: ', title)
#             else:
#                 raise Exception('Unbale to locate title. '+link)
#         del title_soup

#         # extracting image
#         image = source.default_image 	# using default image ( from argument )

#         attribute = 'src'
#         # getting custom attribute if exists
#         if source.image_selector.find('|') >= 0:
#             custom_selector = source.image_selector
#             image_selector = custom_selector.split('|')[0]
#             attribute = custom_selector.split('|')[1]
#             del custom_selector


#         # getting image link from content
#         image_soup = link_soup.select(image_selector, limit=1)
#         if len(image_soup) > 0:
#             # image tag is available
#             if image_soup[0].has_attr(attribute):
#                 image = str(image_soup[0][attribute]).strip()
#                 if checkImageUrl(image):
#                     image = generate_absolute_url(link, image)
#                     # print(f"image is {image}")
#                 else:
#                     # image attribute is empty
#                     image = source.default_image

#         print(f"using headimage: {image}")

#         # alerting if there is no image in all link
#         if source.id in scraped_news:
#             scraped_news[source.id] += 1
#             if image == source.default_image:
#                 image_error[source.id] += 1
#                 #logger.warn('Unable to locate image. Saving default image. '+link)



#         # authorselector = author_selector
#         author = link_soup.select(source.author_selector, limit=1)
        
#         author_img = author[0].find_all('img')
#         author_img = author_img[0]['src'].strip()

#         author_name = author[0].find_all('a')
#         author_name = author_name[0].text.strip()
#         """ author Name index in thahakhabar is 0"""

#         if not author_name:
#             """ author Name index in thahakhabar is 1"""
#             author_name = author[0].find_all('a')
#             author_name = author_name[1].text.strip()

#         new_author = author_schema.Author(
#             author_name = author_name,
#             author_img= author_img,
#             source_id = source.id
#         )

#         author_exists = await search_author(author_name)
#         """ Checking if the author exists in the db"""
#         if not author_exists:
#             print(f"Author: {author_name} not found in db... adding the author..")
#             authorInDB = await create_author(new_author)
#             """ Creating new author in DB"""
#             if not authorInDB:
#                 raise Exception(f'Could not add author, PLEASE CHECK AUTHOR SELECTOR....')
#         else:
#             authorInDB = author_exists
#             print(f"Author: {author_exists} found in DB...")
#         author_id = authorInDB.id
        

#         print(f"author_id : {author_id}")
#         # extracting content
#         content = link_soup.select(source.content_selector, limit=1)
#         if len(content) < 1:
#             raise Exception(f'Content not available or invalid content selector.')
        

#         # getting all content and removing exception from exception_selector
#         content = content[0]

#         addtional_img = [img['src'] for img in content.find_all('img') if img['src'][-4:] != '.gif']
#         if addtional_img:
#             print(f"addtional_imges: {addtional_img}")


#         # for _selector in exception_selector.split(','):
#         #     _selector = _selector.strip()
#         #     if _selector != '':
#         #         exception_soups = content.select(_selector)
#         #         [exception_soup.extract() for exception_soup in exception_soups]

#         # # Removing content images
#         # images = content[0].find_all('img')
#         # [image.extract() for image in images]

#         # # Removing content videos
#         # videos = content[0].find_all('iframe')
#         # [video.extract() for video in videos]

#         """
#         -- Extract only p, ul, ol from content
#         """

#         # collecting all paragraphs as content
#         paragraphs = content.find_all(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'])
#         # paragraphs = content.findChildren(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'], recursive=False)

#         content = [ '' if is_empty_soup(p) else str(p) for p in paragraphs]
#         content = [i for i in content if i] ## removing empty paragraph
#         final_content = [''.join(content)]
        
#         # content_list = []
#         # for c in content:   
#         #     new_content = html2text.html2text(c)
#         #     content_list.append(new_content)  


#         if len(content) < 1:
#             raise Exception('Empty Content.')

#         # Downloading and saving image
#         if not source.debug:
#             # image = saveImage(image)
#             print(f"saving image {image}")

#         # labelselector = ".breadcrumb"
#         label = link_soup.select(source.label_selector, limit=1)
#         label = label[0].find_all('a')[-1].text

#         print(f"label: {label}")
#         if label:
#             print("LABEL FOUND")
#             labelInDb = await get_label_by_name(label)
#             if not labelInDb:
#                 print("NO LABEL IN DB")
#                 labelInDb = await addlabel(label)
#         else:
#             raise Exception(f'No Label found... Please Debug the label selector')

#         del link_soup


#         article =  {
#             # 'id': pk,
#             'url': link,
#             'heading': title,
#             'head_image': image,
#             'content': final_content,
#             'date': str(pubDate),
#             'additional_img': addtional_img,
#             'label_id': labelInDb.id,
#             'source_id': source.id,
#             'like': 0,
#             'shares': 0,
#             'views': 0,
#             'ignores': 0,
#             'total_comments':0,
#             'bookmarks':0,
#             'type': 'latest',
#             'author_id': author_id
#         }

#         print(f"adding article {article} to the database ...")

#         new_article = CreateLatestArticle(**article)
#         article_created = await create_latest_article(new_article)
#         if article_created:
#             print("ARTICLE SUCCESFULLY ADDED")
#         else:
#             raise Exception(f'UNABLE TO ADD ARTICLE TO DB')

#     except RequestException as e:
#         print('Request error. Unable to connect url : '+link)
#         if source.debug:	# Debugging mode
#             return {'error' : 'Request error. Unable to connect url.', 'link': link}

#     except Exception as e:
#         print(str(type(e)) + ' : ' + str(e) +" : "+link)
#         if source.debug:	# Debugging mode
#             return {'error' : str(type(e)) + ' : ' + str(e), 'link': link}




# def checkImageUrl(image_url):
# 	""" 
# 	checks if image_url is valid or not 
# 	"""

# 	if(len(image_url) == 0):
# 		# image url is empty
# 		return False

# 	image_parsed = urlparse(image_url)
# 	if not image_parsed.path:
# 		# image_url doesn't contain any path
# 		return False
# 	return True

# def checkNews(url, prefix):
# 	"""
# 	checking if news with url exists or not
# 	"""
# 	url = url.strip()
# 	if prefix:
# 		pattern = re.compile(prefix)
# 		if not pattern.match(url):
# 			return True
    
# 	# news = News.objects.filter(url=url)

# 	if len(url):
# 		return True
# 	return False



# def generate_absolute_url(link, relative_link):
# 	"""
# 	generating absolute url from relative url
	
# 	Example:
# 	link: http://thakhabar.com/news/18998
# 	relative_link: /images/1039.jpg
# 	return: http://thakhabar.com//images/1039.jpg

# 	"""

# 	root_link = urlparse(link)[0]+'://'+urlparse(link)[1]
# 	if not bool(urlparse(relative_link).netloc) :
# 		if len(relative_link) < 1:
# 			return root_link
# 		if relative_link[0] == '/':
# 			return root_link+relative_link
# 		return root_link+'/'+relative_link
# 	return relative_link


# def is_empty_soup(soup):
# 	return len(soup.contents) <= 0
# 	return len(soup.text.strip()) == 0



