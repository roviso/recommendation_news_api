

def html_giver(recommended_list):
    row_div_open = '<div class="row">'
    col_div_open = '<div class="col">'

    div_close = '</div>'

    def image_div(img_url,url):
        return f' <a href="{url}"> <img src="{img_url}" style="width:20%!important"/></a>'

    def heading(head,url):
        return f'<a href="{url}"><p>{head}</p></a>'

    return_html =  row_div_open 

    for item in recommended_list:
        
        return_html = return_html + col_div_open + image_div(item['head_image'],item['url']) +heading(item['heading'],item['url']) + div_close
    return_html =  return_html + div_close 

    return return_html


def hori_html_formate(recommended_list):
    start_div = ' <div class="container mt-5"><div class="news-slider">'
    div_close = '</div>'
    style = '''<style>
        .news-slider-card {
            position: relative;
            padding: 0px 10px;
        }
        .news-slider .slick-arrow {
            cursor: pointer;
            background-color: #000;
            border-radius: 50%;
            width: 26px;
            height: 26px;
            position: relative;
            color: #fff;
            font-size: 14px;
           
        }

        .news-slider .slick-arrow svg {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .news-slider .slick-slider-prev-btn{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            left: -30px;
            z-index: 1;
        }
        .news-slider .slick-slider-next-btn{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            right: -30px;
            z-index: 1;
        }

        p {
            margin-bottom: 0px;
        }

        .new-slider-card-image {
            position: relative;
            width: 100%;
            height: 260px;
            border-radius: 4px;
        }

        img {
            height: 100%;
            width: 100%;
        }

        .new-slider-card-image-layer {
            position: absolute;
            top: 0;
            right: 0;
            left: 0;
            bottom: 0;
            background-image: linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.9));
            border-radius: 4px;

        }

        .new-slider-card-title {
            position: absolute;
            z-index: 1;
            left: 15px;
            bottom: 15px;
            right: 15px;
        }

        .new-slider-card-title h5 {
            color: #fff;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            font-weight: 400;
            line-height: 30px;
            height: 60px;

        }

        .new-slider-card-category span {
            background-color: #000;
            padding: 3px 6px;
            color: #fff;


        }

        .new-slider-card-date svg {
            margin-right: 10px;
            color: #fafafa;
            font-size: 12px;
        }

        .new-slider-card-date p {
            font-size: 14px;
            color: #fafafa;
            font-weight: 300;
        }
        @media(max-width:575.98px){
            .news-slider .slick-slider-prev-btn{
                left: 0px;
            }
            .news-slider .slick-slider-next-btn{
                right: 0px;
            }
           
        }
        @media(max-width:400.98px){
           
            .news-slider-card{
                padding: 0px 30px;
            }
        }
    </style>'''
    script = '''<script>
    $('.news-slider').slick({
        infinite: true,
        arrows: true,
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 4000,
        prevArrow: '<div class="slick-slider-prev-btn "><span class="fas fa-chevron-left"></span><span class="sr-only ">Prev</span></div>',
        nextArrow: '<div class="slick-slider-next-btn "><span class="fas fa-chevron-right "></span><span class="sr-only ">Next</span></div>',
        responsive: [{
                    breakpoint: 991.98,
                    settings: {
                        slidesToShow: 3,
                    }
                },
                {
                    breakpoint: 767.98,
                    settings: {
                        slidesToShow: 2,
                    }
                },
                {
                    breakpoint: 575.98,
                    settings: {

                        slidesToShow: 2,
                    }
                },
                {
                    breakpoint: 400.98,
                    settings: {

                        slidesToShow: 1,
                    }
                }

            ]
    });
</script>'''



    def make_slider_item(url,head_image,label,heading,date):
        return f'<div class="news-slider-card"><a href="{url}"><div class="new-slider-card-image"><img src="{head_image}"class="card-img-top" alt="..."><div class="new-slider-card-image-layer"><div class="new-slider-card-title "><div class="new-slider-card-category"><span>{label}</span></div><h5>{heading}</h5><div class="new-slider-card-date "><div class="d-flex align-items-center"><i class="fas fa-calendar"></i><p>{date}</p></div></div></div></div></div></a></div>'

    return_html =  start_div

    for item in recommended_list:
        # print(item, dir(item), 55555555555555555555555555555555555555555555555555555555555555)
        # print(item.__dict__, 666666666666666666666666666666666666666666666666666666666666666)
        return_html = return_html + make_slider_item(item.url,item.head_image,item.label,item.heading,item.date)
    
    return_html =  return_html + div_close + div_close + script

    return return_html
