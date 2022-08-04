import requests
from bs4 import BeautifulSoup
from nepali.datetime import nepalidatetime  
from dateutil.parser import parse
from urllib.parse import urlparse
from fastapi import HTTPException
from typing import Optional
from schemas import author_schema
from lxml import etree
from models import source_model


class ScrapeLinkX():
    def __init__(self,source: source_model.Source ,link: str):
        self.link = link
        self.source = source
        CONNECTION_TIMEOUT = 10

        print('Scraping news from link: '+link)

        # Requesting news link
        response = requests.get(link, timeout=CONNECTION_TIMEOUT)
        response.encoding = 'utf-8'
        self.link_soup = BeautifulSoup(response.text, 'html5lib')
        myparser = etree.HTMLParser(encoding="utf-8")
        self.tree = etree.HTML(response.content, parser=myparser)


    def scrape_title(self):
        # getting title
        title_soup = self.link_soup.find("meta", {"property": "og:title"})
        # print(title_soup)
        if title_soup:
            title = str(title_soup['content'])
        else:
            # if meta tag is not available
            title_soup  = self.link_soup.find("title")
            if title_soup:
                title = title_soup.text
            else:
                raise Exception('Unbale to locate title. '+ self.link)
        del title_soup

        return title
      
        

    def scrape_img(self, image_selector:str):
        # print(f'image_selector:{image_selector},999999999999999999')
        img = self.tree.xpath(image_selector)[0].strip()
        if img:
            return img
        else:
            raise Exception('Unbale to locate Head Image. '+ self.link)

    def scrape_author(self,author_name_selector:str, author_img_selector:Optional[str] = None):

        # author = self.link_soup.select(author_selector, limit=1)
        # if not author:
        #     return None
        if author_img_selector :

            author_img = self.tree.xpath(author_img_selector)[0].strip()

            if not author_img:
                Exception('Unbale to locate Author Image. '+ self.link)

        else:
            author_img = self.source.image

        try:
            author_name = self.tree.xpath(author_name_selector)[1].strip()
        except:
            try:
                author_name = self.tree.xpath(author_name_selector)[0].strip()
            except:
                print(f"_________UNABLE TO FIND AUTHOR___________{self.link}___________________")
                author_name = self.source.name

        if not author_name:
            Exception('Unbale to locate Author Name. '+ self.link)


        new_author = author_schema.Author(
            author_name = author_name,
            author_img= author_img,
            source_id = self.source.id
        )

        return new_author

    def scrape_label(self, label_selector: Optional[str] = None):
        if label_selector:
            label = self.tree.xpath(label_selector)[0].strip()

            if not label:
                Exception('Unbale to locate Label :'+ self.link)

            return label
        else:
            return None



    def scrape_content(self, content_selector:str, content_unwanted_selector: str):
        content = self.link_soup.select(content_selector, limit=1)
        if len(content) < 1:
            return None, None
        

        # getting all content and removing exception from exception_selector
        content = content[0]

        addtional_img = [img['src'] for img in content.find_all('img') if img['src'][-4:] != '.gif']
        if addtional_img:
            print(f"addtional_imges: {addtional_img}")

        """
        -- Extract only p, ul, ol from content
        """
        # print(content,11111111111111111111)
        # if content.find(content_unwanted_selector) != None:
        #     content.find(content_unwanted_selector).decompose()
        # print(content,5555555555555555)
        # collecting all paragraphs as content
        paragraphs = content.find_all(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'])
        # paragraphs = content.findChildren(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'], recursive=False)
        

        
        content = [ '' if is_empty_soup(p) else str(p) for p in paragraphs]
        content = [i for i in content if i] ## removing empty paragraph
        final_content = [''.join(content)]

        return final_content,addtional_img
 


    def is_empty_soup(soup):
	    return len(soup.contents) <= 0



class ScrapeLink():
    def __init__(self, link: str):
        self.link = link
        CONNECTION_TIMEOUT = 10

        print('Scraping news from link: '+link)

        # Requesting news link
        response = requests.get(link, timeout=CONNECTION_TIMEOUT)
        response.encoding = 'utf-8'
        self.link_soup = BeautifulSoup(response.text, 'html5lib')


    def scrape_title(self):
        # getting title
        title_soup = self.link_soup.find("meta", {"property": "og:title"})
        # print(title_soup)
        if title_soup:
            title = str(title_soup['content'])
        else:
            # if meta tag is not available
            title_soup  = self.link_soup.find("title")
            if title_soup:
                title = title_soup.text
            else:
                raise Exception('Unbale to locate title. '+ self.link)
        del title_soup

        return title

    def scrape_img(self, image_selector:str):
        attribute = 'src'
        # getting custom attribute if exists
        if image_selector.find('|') >= 0:
            custom_selector = image_selector
            image_selector = custom_selector.split('|')[0]
            attribute = custom_selector.split('|')[1]
            del custom_selector

        image = ''

        # getting image link from content
        image_soup = self.link_soup.select(image_selector, limit=1)
        if len(image_soup) > 0:
            # image tag is available
            if image_soup[0].has_attr(attribute):
                image = str(image_soup[0][attribute]).strip()
                if checkImageUrl(image):
                    image = generate_absolute_url(self.link, image)

        return image


    def scrape_author(self, author_selector:str):

        author = self.link_soup.select(author_selector, limit=1)
        if not author:
            return None

        author_img = author[0].find_all('img')
        author_img = author_img[0]['src'].strip()

        author_name = author[0].find_all('a')
        author_name = author_name[0].text.strip()
        """ author Name index in thahakhabar is 0"""

        if not author_name:
            """ author Name index in thahakhabar is 1"""
            author_name = author[0].find_all('a')
            author_name = author_name[1].text.strip()

        new_author = author_schema.Author(
            author_name = author_name,
            author_img= author_img,
            source_id = 555
        )

        return new_author

    def scrape_label(self, label_selector:str):
        label = self.link_soup.select(label_selector, limit=1)

        if not label:
            return None
        # //div/nav/ol/li[2]/a

        label = label[0].find_all('li')[-1].text



        # label = label[0].find_all('a')[-1].text

        return label

    
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


    def scrape_content(self, content_selector:str, content_unwanted_selector: str):
        content = self.link_soup.select(content_selector, limit=1)
        if len(content) < 1:
            return None, None
        

        # getting all content and removing exception from exception_selector
        content = content[0]

        addtional_img = [img['src'] for img in content.find_all('img') if img['src'][-4:] != '.gif']
        if addtional_img:
            print(f"addtional_imges: {addtional_img}")

        """
        -- Extract only p, ul, ol from content
        """

        if content.find(content_unwanted_selector) != None:
            content.find(content_unwanted_selector).decompose()
        
        # collecting all paragraphs as content
        paragraphs = content.find_all(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'])
        # paragraphs = content.findChildren(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'], recursive=False)

        
        content = [ '' if is_empty_soup(p) else str(p) for p in paragraphs]
        content = [i for i in content if i] ## removing empty paragraph
        final_content = [''.join(content)]

        return final_content,addtional_img
 


    def is_empty_soup(soup):
	    return len(soup.contents) <= 0

async def scrape_normal_rss(test_rss: str):
    """
    Tasks for scraping normal rss
    Collect link from all items and scrape the particular link
    Debug=True for rss debuging
    """
    print("* Scraping normal rss link : " + test_rss)
    try:
        # sending request to the rss link
        r = requests.get(test_rss)
        soup = BeautifulSoup(r.text, "xml")

    except Exception as e:
        print('Error connecting rss url. '+test_rss)
        return {'error' : f'Error connecting url : {e}'}

    # getting all items from rss feed
    items = soup.find_all('item')
    if len(items) == 0:
        print('No items available in rss feed. '+test_rss)

    links = {}


    for item in reversed(items):
        # published date (default current date)
        try:
            pubDate = item.find('pubDate').get_text()
            pubDate = nepalidatetime.from_datetime(parse(str(pubDate)))
        except:
            pubDate = nepalidatetime.now()

        # getting link from item
        link = item.find('link')
        if not link:
            # if the item has no link
            print('Unable to find link in rss item. '+link)
        link = link.text.strip()

        links.update({link:str(pubDate)})

    return links
    
def scrape_title(link: str):
    """
    Scrapes and saves news from news link
    Content selector, image selector, label selector is strictly required
    """
    # link = "https://www.thahakhabar.com/news/78710"
    CONNECTION_TIMEOUT = 10

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
        print('title: ', title)
    else:
        # if meta tag is not available
        title_soup  = link_soup.find("title")
        if title_soup:
            title = title_soup.text
            print('title: ', title)
        else:
            raise Exception('Unbale to locate title. '+link)
    del title_soup

    return title


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



def scrape_img(link: str, image_selector:str):
    """
    Scrapes and saves news from news link
    Content selector, image selector, label selector is strictly required
    """
    # link = "https://www.thahakhabar.com/news/78710"
    CONNECTION_TIMEOUT = 10
    
    print('Scraping news from link: '+link)

    # Requesting news link
    response = requests.get(link, timeout=CONNECTION_TIMEOUT)
    response.encoding = 'utf-8'
    link_soup = BeautifulSoup(response.text, 'html5lib')

    attribute = 'src'
    # getting custom attribute if exists
    if image_selector.find('|') >= 0:
        custom_selector = image_selector
        image_selector = custom_selector.split('|')[0]
        attribute = custom_selector.split('|')[1]
        del custom_selector

    image = ''

    # getting image link from content
    image_soup = link_soup.select(image_selector, limit=1)
    if len(image_soup) > 0:
        # image tag is available
        if image_soup[0].has_attr(attribute):
            image = str(image_soup[0][attribute]).strip()
            if checkImageUrl(image):
                image = generate_absolute_url(link, image)

    return image




def scrape_author(link: str, author_selector:str):
    """
    Scrapes and saves news from news link
    Content selector, image selector, label selector is strictly required
    """
    # link = "https://www.thahakhabar.com/news/78710"
    CONNECTION_TIMEOUT = 10
    
    print('Scraping news from link: '+link)

    # Requesting news link
    response = requests.get(link, timeout=CONNECTION_TIMEOUT)
    response.encoding = 'utf-8'
    link_soup = BeautifulSoup(response.text, 'html5lib')

    author = link_soup.select(author_selector, limit=1)

    print(author,55555555555555555555)
        
    author_img = author[0].find_all('img')
    author_img = author_img[0]['src'].strip()

    author_name = author[0].find_all('a')
    author_name = author_name[0].text.strip()
    """ author Name index in thahakhabar is 0"""

    if not author_name:
        """ author Name index in thahakhabar is 1"""
        author_name = author[0].find_all('a')
        author_name = author_name[1].text.strip()

    new_author = author_schema.Author(
        author_name = author_name,
        author_img= author_img,
        source = "source_name"
    )

    return new_author



def is_empty_soup(soup):
	return len(soup.contents) <= 0
	return len(soup.text.strip()) == 0



def scrape_content(link:str, content_selector:str, content_unwanted_selector: str):
    """
    Scrapes and saves news from news link
    Content selector, image selector, label selector is strictly required
    """
    # link = "https://www.thahakhabar.com/news/78710"
    CONNECTION_TIMEOUT = 10
    
    print('Scraping news from link: '+link)

    # Requesting news link
    response = requests.get(link, timeout=CONNECTION_TIMEOUT)
    response.encoding = 'utf-8'
    link_soup = BeautifulSoup(response.text, 'html5lib')


    content = link_soup.select(content_selector, limit=1)
    if len(content) < 1:
        raise Exception(f'Content not available or invalid content selector.')
    

    # getting all content and removing exception from exception_selector
    content = content[0]

    addtional_img = [img['src'] for img in content.find_all('img') if img['src'][-4:] != '.gif']
    if addtional_img:
        print(f"addtional_imges: {addtional_img}")

    """
    -- Extract only p, ul, ol from content
    """

    if content.find(content_unwanted_selector) != None:
        content.find(content_unwanted_selector).decompose()
    
    # collecting all paragraphs as content
    paragraphs = content.find_all(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'])
    # paragraphs = content.findChildren(['p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure'], recursive=False)

    
    content = [ '' if is_empty_soup(p) else str(p) for p in paragraphs]
    content = [i for i in content if i] ## removing empty paragraph
    final_content = [''.join(content)]

    return {'content': final_content,
            'additional_img': addtional_img}




def scrape_label(link:str, label_selector:str):
    """
    Scrapes and saves news from news link
    Content selector, image selector, label selector is strictly required
    """
    # link = "https://www.thahakhabar.com/news/78710"
    CONNECTION_TIMEOUT = 10
    
    print('Scraping news from link: '+link)

    # Requesting news link
    response = requests.get(link, timeout=CONNECTION_TIMEOUT)
    response.encoding = 'utf-8'
    link_soup = BeautifulSoup(response.text, 'html5lib')

    label = link_soup.select(label_selector, limit=1)
    label = label[0].find_all('a')[-1].text

    return label



# def test_source_scrape()