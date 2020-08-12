#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import ssl

# For ignoring SSL certificate errors
class scrape_class:
    def __init__(self,product_url):
        self.url = product_url
        self.product_json = {}

    # This block of code will help extract the Brand of the item
    def getBrand(self,soup):
        print("test brand")
        for divs in soup.findAll('div', attrs={'class': 'a-box-group'}):
            print("divs")
            try:
                self.product_json['brand'] = divs['data-brand']
                print(divs)
                break
            except:
                pass

    # This block of code will help extract the Prodcut Title of the item
    def getProductTitle(self,soup):
        for spans in soup.findAll('span', attrs={'id': 'productTitle'}):
            name_of_product = spans.text.strip()
            self.product_json['name'] = name_of_product
            break

    # This block of code will help extract the price of the item in dollars
    def getPrice(self,soup):
        for divs in soup.findAll('div'):
            try:
                price = str(divs['data-asin-price'])
                self.product_json['price'] = '$' + price
                break
            except:
                pass

    # This block of code will help extract the image of the item in dollars
    def getImage(self,soup):
        for divs in soup.findAll('div', attrs={'id': 'rwImages_hidden'}):
            for img_tag in divs.findAll('img', attrs={'style': 'display:none;'
                                        }):
                self.product_json['img-url'] = img_tag['src']
                break

    # This block of code will help extract the average star rating of the product
    def getAverageRating(self,soup):
        for i_tags in soup.findAll('i',
                                   attrs={'data-hook': 'average-star-rating'}):
            for spans in i_tags.findAll('span', attrs={'class': 'a-icon-alt'}):
                self.product_json['star-rating'] = spans.text.strip()
                break

    # This block of code will help extract the number of customer reviews of the product
    def getReviewCount(self,soup):
        for spans in soup.findAll('span', attrs={'id': 'acrCustomerReviewText'
                                  }):
            if spans.text:
                review_count = spans.text.strip()
                self.product_json['customer-reviews-count'] = review_count
                break

    # This block of code will help extract top specifications and details of the product
    def getDetails(self,soup):
        self.product_json['details'] = []
        for ul_tags in soup.findAll('ul',
                                    attrs={'class': 'a-unordered-list a-vertical a-spacing-none'
                                    }):
            for li_tags in ul_tags.findAll('li'):
                for spans in li_tags.findAll('span',
                        attrs={'class': 'a-list-item'}, text=True,
                        recursive=False):
                    self.product_json['details'].append(spans.text.strip())

    # This block of code will help extract the long reviews of the product
    def getReviews(self,soup):
        self.product_json['reviews'] = []
        for divs in soup.findAll('div', attrs={'data-hook': 'cmps-review-collapsed'
                                 }):

            self.product_json['reviews'].append(divs.text)
        print(self.product_json['reviews'])

    def scrape_reviews(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        html = urllib.request.urlopen(self.url, context=ctx).read()
        soup = BeautifulSoup(html, 'html.parser')
        self.product_json['url'] = self.url
        self.getBrand(soup)
        self.getProductTitle(soup)
        self.getPrice(soup)
        self.getAverageRating(soup)
        self.getReviewCount(soup)
        self.getDetails(soup)
        self.getReviews(soup)
        return self.product_json