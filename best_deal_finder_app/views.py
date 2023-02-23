import locale
import re

from django.utils.decorators import method_decorator


from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


DATA_CONFIG = [
    {
        'website': 'amazon',
        'url': 'https://www.amazon.com/s?k=laptop&i=electronics&crid=3C0S4NZKOWBS2&sprefix=laptop%2Celectronics%2C103&ref=nb_sb_noss_1',
        'row': {
            'element': 'div',
            'class': 's-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 AdHolder sg-col s-widget-spacing-small sg-col-12-of-16'
        },
        'name': {
            'element': 'span',
            'class': 'a-size-medium'
        },
        'price': {
            'element': 'span',
            'class': 'a-price-whole'
        },
        'rating': {
            'element': 'span',
            'class': 'a-size-base'
        },
        'link': {
            'element': 'a',
            'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'
        },
        'image': {
            'element': 'img',
            'class': 's-image',
            'prefix': ''
        },
    },
    {
        'website': 'ebay',
        'url': 'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=laptop&_sacat=0',
        'row': {
            'element': 'div',
            'class': 'srp-river-results clearfix'
        },
        'name': {
            'element': 'div',
            'class': 's-item__title'
        },
        'price': {
            'element': 'span',
            'class': 's-item__price'
        },
        'rating': {
            'element': 'div',
            'class': 'clipped'
        },
        'link': {
            'element': 'a',
            'class': 's-item__link',
            'prefix': ''
        },
        'image': {
            'element': 'img',
            'class': 's-item__image-img'
        },
    },
    {
        'website': 'costco',
        # 'url': 'https://www.costco.com/CatalogSearch?dept=All&keyword=laptop',
        'url': 'https://www.costco.com/laptops.html',
        'row': {
            'element': 'div',
            'class': 'product'
                },
        'name': {
            'element': 'a',
            'class': ''
        },
        'price': {
            'element': 'div',
            'class': 'price'
        },
        'rating': {
            'element': 'span',
            'class': 'offscreen'
        },
        'link': {
            'element': 'a',
            'class': '',
            'prefix': ''
        },
        'image': {
            'element': 'img',
            'class': 'img-responsive'
        },
    },
    {
        'website': 'bestbuy',
        # 'url': 'https://www.bestbuy.com/site/searchpage.jsp?st=laptop&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys',
        'url': 'https://www.bestbuy.com/site/promo/laptop-and-computer-deals?qp=category_facet%3DAll%20Laptops~pcmcat138500050001',
        'row': {
            'element': 'div',
            'class': 'shop-sku-list-item'
        },
        'name': {
            'element': 'a',
            'class': ''
        },
        'price': {
            'element': 'span',
            'class': 'sr-only'
        },
        'rating': {
            'element': 'p',
            'class': 'visually-hidden'
        },
        'link': {
            'element': 'a',
            'class': '',
            'prefix': 'https://www.bestbuy.com'
        },
        'image': {
            'element': 'img',
            'class': 'product-image'
        },
    },
{
        'website': 'walmart',
        # 'url': 'https://www.walmart.com/shop/deals/electronics/computers?cat_id=3944_3951_1089430_132960',
        'url': 'https://www.walmart.com/browse/electronics/all-laptop-computers/3944_3951_1089430_132960',
        'row': {
            'element': 'div',
            'class': 'mb1 ph1 pa0-xl bb b--near-white w-25'
                },
        'name': {
            'element': 'span',
            'class': 'w_iUH7'
        },
        'price': {
            'element': 'div',
            'class': 'mr1 mr2-xl b black green lh-copy f5 f4-l'
        },
        'rating': {
            'element': 'span',
            'class': 'black inline-flex mr1'
        },
        'link': {
            'element': 'a',
            'class': 'absolute w-100 h-100 z-1 hide-sibling-opacity',
            'prefix': 'https://www.walmart.com'
        },
        'image': {
            'element': 'img',
            'class': 'absolute top-0 left-0'
        },
    },
]


@method_decorator(csrf_exempt, name='dispatch')
class BestDealFinder(View):
    def get(self, request):
        search_product_name = request.GET.get('product_name')
        search_product_name_sub_str = search_product_name.split()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        products_data = []
        for product_data_config in DATA_CONFIG:
            driver.get(product_data_config['url'])
            content = driver.page_source
            soup = BeautifulSoup(content, features="html.parser")
            all_rows = soup.findAll(product_data_config['row']['element'], attrs={'class': product_data_config['row']['class']})
            for a in all_rows:
                name = a.find(product_data_config['name']['element'], attrs={'class': product_data_config['name']['class']})
                if name:
                    if all(s in name.text.lower() for s in search_product_name_sub_str):
                        price = a.find(product_data_config['price']['element'], attrs={'class': product_data_config['price']['class']})
                        decimal_point_char = locale.localeconv()['decimal_point']
                        if price:
                            price_value = re.sub(r'[^0-9' + decimal_point_char + r']+', '', str(price.text.strip()))
                            if price_value != '':
                                if product_data_config['link']['prefix']:
                                    link_prefix = product_data_config['link']['prefix']
                                else:
                                    link_prefix = ''
                                rating = a.find(product_data_config['rating']['element'],
                                                attrs={'class': product_data_config['rating']['class']})
                                link = a.find(product_data_config['link']['element'],
                                              attrs={'class': product_data_config['link']['class']})
                                image = a.find(product_data_config['image']['element'],
                                               attrs={'class': product_data_config['image']['class']})
                                products_data.append({
                                    'product_name': name.text.strip(),
                                    'product_price': float(price_value),
                                    'product_rating': rating.text.strip(),
                                    'product_link': link_prefix + link['href'],
                                    'product_image': image['src'] if image['src'] else ''
                                })

        products_data.sort(key=lambda x: x['product_price'])

        data = {
            "best-product-deal-data-list": products_data,
        }
        print(data)
        return JsonResponse(data)
