## Start venv
.\apienv\Scripts\activate


## To restart postgress
systemctl restart postgresql

## to kill process

sudo kill -9 `sudo lsof -t -i:8000`

## to Start celery scrapping
celery worker -A tasks -P celery_pool_asyncio:TaskPool --scheduler celery_pool_asyncio:PersistentScheduler
celery beat -A tasks --scheduler celery_pool_asyncio:PersistentScheduler

## Required Files:
 - 

git@Qz55y1wty868vFfp5e7d:raviprajapati/recommendation_news_api.git
https://Qz55y1wty868vFfp5e7d/raviprajapati/recommendation_news_api.git
<!-- delete from "article" where type="latest" -->

{
    "updated_at": null,
    "content_selector": ".news-detail-content",
    "analytics_id": "UA-125866437-1",
    "deleted_at": null,
    "exception_selector": "",
    "category_id": 0,
    "name": "farakdar",
    "priority": 0,
    "pubDate": "",
    "image": "https://fdcdn.prixa.net/media/albums/logo_for_website_Y6ZGNlriAS_adKxUhM1cf.png",
    "image_selector": "meta[property='og:image']|content",
    "debug": false,
    "domain": "farakdhar.com",
    "author_selector": ".news-info",
    "debug_link": null,
    "id": 1,
    "link": "https://farakdhar.com/hamro-rss",
    "label_selector": ".breadcrumb",
    "disable": false,
    "created_at": null,
    "link_prefix": "",
    "default_image": "",
    "link_type": "normal_rss"
}



4skp-2Zem2gA-o_RSzKM25RLyAFmFTEXo--ClihGFNQ : {
        ip--Mn-Np0wnV124iWYhESxGSM2QbU327tKnDJk4b9E,
        uu5eNiuFIzPSt3P7PiYBnatu9PTxuqm4UBrQucn-d2Y,
        e7sWoH2yUJQBbItQ5IubuE_nPF3AIzj_irTKsCHVKVI,
        HH7-GSG_YYjP1CV3cf_ICf5RGWanA_lxrhYBf9JDx5k,


}


ibpKHKHi54s3atX_GDmQoL5wxyMyxqTsH4Qrw_kAVeA: { 
    HH7-GSG_YYjP1CV3cf_ICf5RGWanA_lxrhYBf9JDx5k,
    ip--Mn-Np0wnV124iWYhESxGSM2QbU327tKnDJk4b9E,

}


3FrWlo9gX9DtV9LaLdpeTGt8BuWs-Jy05RRwxk4QjmY: {
    HH7-GSG_YYjP1CV3cf_ICf5RGWanA_lxrhYBf9JDx5k,
    UY4nPHr3GnlaC9bgdqRZNZCS6uLFTozqnY3QFe900hc,
    FEOZXs4ma802LO5EiJpavOhWjht55cYfmt9EFIhnGsQ,
    zFTdnWdF6M-ZujlWxzMMOr7kuD2b4-hr7_mmLMfzcDA,
    5aNvdjEv_h26yc4wW7hRYMOVFZEhlGLSsXXRmktT5jo

}


similar api not giving list of news.
