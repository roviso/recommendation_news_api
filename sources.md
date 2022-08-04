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
  "name": "फरक धार",
  "image": "https://fdcdn.prixa.net/media/albums/logo_for_website_Y6ZGNlriAS_adKxUhM1cf.png",
  "domain": "farakdhar.com",
  "link": "https://farakdhar.com/hamro-rss",
  "content_selector": ".news-detail-content",
  "image_selector": "/html/body/section[4]/div/div/div[1]/div/div[3]/div[3]/img/@src",
  "author_img_selector": "/html/body/section[4]/div/div/div[1]/div/div[3]/div[2]/div[1]/div/div/div[1]/img/@src",
  "author_name_selector": "/html/body/section[4]/div/div/div[1]/div/div[3]/div[2]/div[1]/div/div/div[2]/div/div[1]/a/text()",
  "label_selector": "/html/body/section[4]/div/div/div[1]/div/nav/ol/li[2]/a/text()",
  "disable": false,
  "analytics_id": "UA-125866437-1"
}


{
  "name": "ICT Samachar",
  "image": "https://ictsamachar.com/uploads/logo/969971682ictlogo123.png",
  "domain": "ictsamachar.com",
  "link": "https://ictsamachar.com/feed",
  "content_selector": ".module-detail-page > section",
  "image_selector": "/html/body/div[3]/div/div/div[1]/article[1]/section/figure/img/@src",
  "author_img_selector": "/html/body/div[3]/div/div/div[1]/article[1]/header/ul/li[1]/img/@src",
  "author_name_selector": "/html/body/div[3]/div/div/div[1]/article[1]/header/ul/li[1]/a/text()",
  "label_selector": "/html/body/div[3]/div/div/div[1]/article[1]/header/div[1]/a/text()",
  "disable": false,
  "analytics_id": "UA-80504020-1"
}


{
  "name": "बीबीसी नेपाली",
  "image": "https://news.files.bbci.co.uk/ws/img/logos/og/nepali.png",
  "domain": "bbc.com",
  "link": "http://feeds.bbci.co.uk/nepali/rss.xml",
  "content_selector": ".essoxwk0",
  "image_selector": "//div[contains(@class,'ezb2r2b0')]/picture/img/@src",
  "author_img_selector": "",
  "author_name_selector": "//div[contains(@class,'e11nzto4')]/ul/li[1]/text()",
  "label_selector": "",
  "disable": false,
  "analytics_id": "string"
}


{
  "name": "सेतोपाटी",
  "image": "https://www.setopati.com/themes/setopati/images/logo.svg?v=1.9",
  "domain": "setopati.com",
  "link": "https://setopati.com/feed",
  "content_selector": ".editor-box",
  "image_selector": "/html/body/div[7]/div/section/div[2]/div/figure/img/@src",
  "author_img_selector": "/html/body/div[7]/div/section/div[1]/div/div[1]/div/div[1]/img/@src",
  "author_name_selector": "/html/body/div[7]/div/section/div[1]/div/div[1]/div/div[2]/h2/a/text()",
  "label_selector": "/html/body/div[4]/div/header/div[1]/div[1]/div/a/figure/span/text()",
  "disable": false,
  "analytics_id": "string"
}

{
  "name": "लोकान्तर",
  "image": "https://lktcdn.prixacdn.net/media/lokaantar_nepali_logo_Final_ULGccioncf.png",
  "domain": "lokaantar.com",
  "link": "http://lokaantar.com/rss",
  "content_selector": ".detail-content",
  "image_selector": "/html/body/main/section[2]/div/div[1]/div/div[2]/div[6]/div[1]/img/@src",
  "author_img_selector": "/html/body/main/section[2]/div/div[1]/div/div[2]/div[4]/div[1]/div[1]/img/@src",
  "author_name_selector": "/html/body/main/section[2]/div/div[1]/div/div[2]/div[4]/div[1]/div[2]/div/p/span/a/text()",
  "label_selector": "/html/body/main/section[2]/div/div[1]/div/div[1]/div/nav/ol/li[2]/a/text()",
  "disable": false,
  "analytics_id": "string"
}


{
  "name": "उज्यालो अनलाईन",
  "image": "https://unncdn.prixacdn.net/static/frontend/img/text_logo.png",
  "domain": "ujyaaloonline.com",
  "link": "https://ujyaaloonline.com/rss",
  "content_selector": ".imgAdj",
  "image_selector": "/html/body/section/div/div/div[3]/div[2]/figure/img/@src",
  "author_img_selector": "",
  "author_name_selector": "/html/body/section/div/div/div[3]/div[2]/div[1]/div[1]/a/text()",
  "label_selector": "/html/body/section/div/div/div[3]/nav/ol/li[2]/text()",
  "disable": false,
  "analytics_id": "string"
}

{
    "name": "थाहाखबर",
    "image": "https://thahacdn.prixacdn.net/static/frontend/images/logo.png",
    "link": "https://thahakhabar.com/rss",
    "image_selector": "/html/body/section[3]/div/div[3]/div[1]/div[2]/div/a/img/@src",
    "author_name_selector": "/html/body/section[3]/div/div[2]/div[3]/div[1]/div[2]/a/b/text()",
    "analytics_id": "string",
    "domain": "thahakhabar.com",
    "content_selector": ".detail-news-details-paragh",
    "author_img_selector": "/html/body/section[3]/div/div[2]/div[3]/div[1]/div[1]/a/img/@src",
    "label_selector": "/html/body/section[3]/div/div[1]/nav/ol/li[2]/a/text()",
    "disable": false
}


{
  "name": "नेपालखबर",
  "image": "https://nepalkhabar.prixacdn.net/static/normal/images/assets/nklogonew.svg",
  "domain": "nepalkhabar.com",
  "link": "https://nepalkhabar.com/index.php",
  "content_selector": ".uk-article",
  "image_selector": "/html/body/div[8]/div[2]/div/div/div/div[1]/div[1]/div[2]/div/img/@src",
  "author_img_selector": "",
  "author_name_selector": "/html/body/div[8]/div[2]/div/div/div/div[1]/div[2]/div/div/div/div[1]/div/div/div[2]/a/span/text()",
  "label_selector": "",
  "disable": false,
  "analytics_id": "UA-80504020-1"
}
