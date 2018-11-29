# -*- coding: utf-8 -*-
import scrapy
import json
import requests,re
from scrapy.http import Request
from lxml import etree
import os
import chardet
from ..items import *
class GaolaSpider(scrapy.Spider):
    name = 'gaola'
    # allowed_domains = ['dsdsds']
    start_urls = ['https://www.kaola.com/getFrontCategory.shtml?xRequestedWith=XMLHttpRequest']

    def parse(self, response):
        # print(response.text)
        text = response.text
        sid = json.loads(text)['frontCategoryList']
        for i in range(0,len(sid)):
            did = sid[i]['childrenNodeList']
            for j in range(0, len(did)):
                # print(did[j]['categoryName'],did[j]['categoryId'])
                for i in range(1,100):
                    zurl = 'https://www.kaola.com/category/'+str(did[j]['categoryId'])+'.html?key=&pageSize=60&pageNo='+str(i)+'&sortfield=0&isStock=false&isSelfProduct=false&isPromote=false&isTaxFree=false&factoryStoreTag=-1&isDesc=true&b=&proIds=&source=false&country=&needBrandDirect=false&isNavigation=0&lowerPrice=-1&upperPrice=-1&backCategory=&headCategoryId=&#topTab'
                    # print(zurl)
                    yield Request(zurl,callback=self.Urls)
    def Urls(self,response):
        print(response.url)
        surl = response.xpath('//*[@id="result"]/li/div/div/div/a/@href').extract()
        # a = []
        # a.append(len(surl))
        # print(a)
        price = response.xpath('//*[@id="result"]/li/div/div/p[1]/span[1]/text()').extract()
        name = response.xpath('//*[@id="result"]/li/div/div/div/a/h2/text()').extract()

        for i in range(0,len(surl)):
            urls = 'https://goods.kaola.com'+surl[i]
            yield Request(urls,callback=self.Text,meta={'names':name[i],'prices':price[i]})
    def Text(selfs,response):
            # print(urls)
            # xurls = requests.get(urls).text
            # print(xurls)
            sid = re.compile("ecomm_prodid:'(.*?)',").findall(response.text)
            lei = re.compile('ecomm_pcat:(.*?),').findall(response.text)
            leis = re.compile('ecomm_pvalues:(.*?),').findall(response.text)
            if lei[0][2:-2] == []:
                ls = leis[0][2:-2]
            else:
                ls =  lei[0][2:-2]
            img = etree.HTML(response.text).xpath('//*[@id="showImgBox"]/img/@src')
            imgs = 'http:'+img[0]

            ping = etree.HTML(response.text).xpath('//*[@id="commentCounts"]/text()')
            dian = re.compile("brand: '(.*?)',").findall(response.text)
            # print(ls)
            xiao = re.compile('<b id="commentCounts" class="commentCount v1 v0">(.*?)</b>').findall(response.text)[0]
            dicts = {'platform':11,'goods_name':response.meta['names'],'goods_cate_name':ls,'goods_image':imgs,'goods_detail_url':response.url,'goods_product_id':sid[0],'goods_price':response.meta['prices'],'goods_sale_num':xiao,'goods_total_score':ping[0],'shop_name':dian[0]}
            print(response.meta['prices'])
            return_list = []
            return_list.append(dicts)
            base_dir = os.getcwd()
            filename = os.path.join(base_dir, 'news.json')
            data = {"info": "操作完成",
                    "code": 200,
                    "data": return_list
                    }
            with open(filename, 'a', encoding='utf-8') as f:
                line = json.dumps(data, ensure_ascii=False)+'\n'
                f.write(line)
                print(line)
                data_info  = json.dumps(data)
                form_data = {"data":data_info}
                url = 'http://bgpy.wantupai.com/server/api/goods/import'
                ab  = requests.post(url,data=form_data)
                print(ab.text)
            return dicts
