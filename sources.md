Source Testing:
Input: [Dict({column: data})]

Step1: Check column.link working or not
    RequestURL: /scrap/test_rss/
    response: {link: pubdate}
    if response:
        "Working"

Step1.5: Get Source image
    Go to one of the link 
    Inspect to the logo
    Copy img src : <img src="https://ictsamachar.com/uploads/logo/969971682ictlogo123.png"> : https://ictsamachar.com/uploads/logo/969971682ictlogo123.png

Step2: Add Source to database:
    RequestURL: /source/add_source
    RequestBody: Input[index]
    response: Null 

Step3: Check SourceId
    RequestURL: /source/get_source
    response: [Input]
    Get the "source_id" of recently added source 

Step4: 
    RequestURL: scrap/test_source_scrape
    source_id: source_id
    response: {
                "rss_link": "https://www.corporatenepal.com/rss/",
                "test_link": "https://corporatenepal.com/story/230604",
                "title": "गुरुपूर्णिमाः मानस पटलमा अनेकौं गुरुका संस्मरण",
                "head_image": "https://corporatenepalcdn.prixacdn.net/media/gallery_folder/diwakar-panta_uPOcSkuyFV..jpg",
                "author": {
                    "author_name": "ज्यो. गुरु दिवाकर पन्त",
                    "author_img": "https://corporatenepalcdn.prixacdn.net/media/gallery_folder/diwakar-panta_uPOcSkuyFV..jpg",
                    "source": "source_name"
                },
                "content": [
                    "<p>म र अर्का एक जना साथी चितवन आँखा अस्पताल अघि डेरामा बस्थ्यौँ ।"
                ],
                "additional_img": [],
                "label": "विचार"
                }
    Check all the link





{
    "id": 1,
    "name": "farakdar",
    "domain": "farakdhar.com",
    "link": "https://farakdhar.com/hamro-rss",
    "link_type": "normal_rss",
    "image": "https://fdcdn.prixa.net/media/albums/logo_for_website_Y6ZGNlriAS_adKxUhM1cf.png",
    "author_selector": ".news-info",
    "image_selector": "meta[property='og:image']|content",
    "label_selector": ".breadcrumb",
    "content_selector": ".news-detail-content",
    "analytics_id": "UA-125866437-1",


    "exception_selector": "",
    "debug": false,
    "debug_link": null,
    "disable": false,
    "link_prefix": "",
    "default_image": "",
    "category_id": 0,
    "pubDate": "",
    "priority": 0
}



{
  "name": "नेपालखबर",
  "domain": "nepalkhabar.com",
  "link": "https://nepalkhabar.com/index.php",
  "link_type": "normal_rss",
  "image": "https://nepalkhabar.prixacdn.net/static/normal/images/assets/nklogonew.svg",
  "author_selector": "string",
  "image_selector": ".single-article-intro-image img",
  "label_selector": "string",
  "content_selector": ".uk-article",
  "analytics_id": "UA-80504020-1",


  "category_id": 0,
  "link_prefix": "",
  "priority": 0,
  "exception_selector": "",
  "default_image": "",
  "pubDate": "",
  "debug": false,
  "disable": false
}


{
  "name": "",
  "domain": "nepalkhabar.com",
  "link": "https://corporatenepal.com/rss/",
  "link_type": "normal_rss",
  "image": "https://nepalkhabar.prixacdn.net/static/normal/images/assets/nklogonew.svg",
  "author_selector": "string",
  "image_selector": ".single-article-intro-image img",
  "label_selector": "string",
  "content_selector": ".uk-article",
  "analytics_id": "UA-80504020-1",


  "category_id": 0,
  "link_prefix": "",
  "priority": 0,
  "exception_selector": "",
  "default_image": "",
  "pubDate": "",
  "debug": false,
  "disable": false
}
