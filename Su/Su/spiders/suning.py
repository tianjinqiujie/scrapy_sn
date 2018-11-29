# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
import requests
from lxml import etree
import json
import os
class SuningSpider(scrapy.Spider):
    name = 'suning'
    # allowed_domains = ['sdfsafas']
    start_urls = ['https://lib.suning.com/api/jsonp/cb/sortList_v6-threeSortLoad.jsonp?callback=threeSortLoad']#获取接口

    def parse(self, response):
        lname = re.compile('"elementName":"(.*?)"').findall(response.text)#获取名字
        for i in range(0,len(lname)):#遍历名字
            lurl = 'https://search.suning.com/emall/searchV1Product.do?keyword='+str(lname[i])+'&ci=0&pg=01&cp=1&il=0&st=0&iy=0&adNumber=0&n=1&sesab=ACAABAAB&id=IDENTIFYING&cc=010&paging='+str(i)+'&sub=0'#接口拼接
            turl = requests.get(lurl).text
            url  = etree.HTML(turl).xpath('//*[@class="img-block"]/a/@href')
            if url == []:
                pass
            else:
                for j in range(0,len(url)):
                    xurl  = 'https:'+url[j]
                    yield Request(xurl,callback=self.SUrl)
    def SUrl(self,response):
        name = response.xpath('//*[@id="itemDisplayName"]/text()').extract()
        if len(name) == 1:
            names = name[0]
        else:
            names = name[1]
        lei  =  response.xpath('//*[@id="category1"]/text()').extract()
        dian = re.compile('"flagshipName":"(.*?)",',re.S).findall(response.text)[0]

        partNumber = re.compile('"partNumber":(.*?),').findall(response.text)
        category1 = re.compile('"category1":(.*?),').findall(response.text)
        catenIds = re.compile('"catenIds":(.*?),').findall(response.text)
        brandId = re.compile('"brandId":(.*?),').findall(response.text)
        flagshipid = re.compile('"flagshipid":(.*?),').findall(response.text)
        vendorCode = re.compile('"vendorCode":(.*?),').findall(response.text)
        ninePartNumber = re.compile('"ninePartNumber":(.*?),').findall(response.text)
        sids = flagshipid[0][1:-1]
        urls = "https://pas.suning.com/nspcsale_0_"+partNumber[0][1:-1]+"_"+partNumber[0][1:-1]+"_"+flagshipid[0][1:-1]+"_10_010_0100101_"+category1[0][1:-1]+"_1000000_9017_10106_Z001___"+catenIds[0][1:-1]+"_"+brandId[0][1:-1]+".html?callback=pcData&_=1541748498055"
        purl = requests.get(urls).text
        price  = re.compile('"netPrice":"(.*?)",',re.S).findall(purl)
        sping  = re.compile('<span id="chead_qualityStar">商品满意度：(.*?)分</span>',re.S).findall(response.text)
        plurl = 'https://review.suning.com/ajax/review_satisfy/package-'+ninePartNumber[0][1:-1]+'-'+vendorCode[0][1:-1]+'-----satisfy.htm?callback=satisfy'
        ps = requests.get(plurl).text
        xiao = re.compile('"totalCount":(.*?),').findall(ps)
        if xiao == []:
            xiaos = 0
        else:
            xiaos = xiao[0]
        if  sping ==[]:
            ping = 0 or 4 or 3
        else:
            ping = sping[0]
        img = re.compile('<meta property="og:image" content="(.*?)"/>',re.S).findall(response.text)
        imgs = 'https:'+img[0]

        # print(name[1],lei[0],dian,price[0],ping,lei[0],imgs,sid[0],response.url,dian,xiaos)
        dicts = {'platform': 5, 'goods_name': names, 'goods_cate_name': lei[0], 'goods_image': imgs,'goods_detail_url': response.url, 'goods_product_id': sids, 'goods_price': price[0],'goods_sale_num': xiaos, 'goods_total_score': ping, 'shop_name': dian}
        return_list = []
        return_list.append(dicts)
        base_dir = os.getcwd()
        filename = os.path.join(base_dir, 'news.json')
        data = {"info": "操作完成",
                "code": 200,
                "data": return_list
                }
        with open(filename, 'a', encoding='utf-8') as f:
            line = json.dumps(data, ensure_ascii=False) + '\n'
            f.write(line)
            # print(line)
            data_info = json.dumps(data)
            form_data = {"data": data_info}
            url = 'http://bgpy.wantupai.com/server/api/goods/import'
            ab = requests.post(url, data=form_data)
            print(ab.text)
        return dicts
