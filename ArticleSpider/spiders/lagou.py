# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5
from datetime import datetime


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            # 'Cookie': 'user_trace_token=20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
            'Cookie': '_ga=GA1.2.150832338.1544948862; user_trace_token=20181216162740-73d4b791-010c-11e9-8d2a-5254005c3644; LGUID=20181216162740-73d4bec9-010c-11e9-8d2a-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; _gid=GA1.2.1665562449.1545142740; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22167c1f6c6563f2-0200087c7010ae-6313363-1440000-167c1f6c65717b%22%2C%22%24device_id%22%3A%22167c1f6c6563f2-0200087c7010ae-6313363-1440000-167c1f6c65717b%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; ab_test_random_num=0; hasDeliver=0; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; SEARCH_ID=401304022d50431f9c3aae385d107259; JSESSIONID=ABAAABAAAIAACBIE3C51075A8F844A3D9E5219EE9611B73; _gat=1; LGSID=20181220165036-51a0d005-0434-11e9-b480-525400f775ce; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DeYk71yqmDs1nTD-OUc4MCHZKHhwiokQGkekuJZWtX-S%26ck%3D5751.1.91.261.146.261.145.292%26shh%3Dwww.baidu.com%26wd%3D%26eqid%3Dd8af1f280005467b000000055c1b57d9; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1544948862,1545142739,1545229706,1545295839; _putrc=3626FC9C1A69937D123F89F2B170EADC; login=true; unick=%E6%8B%89%E5%8B%BE%E7%94%A8%E6%88%B78316; gate_login_token=f2a03f30bb6312dc4c2a39487a3d6a4f4b07a28fdcc85b8e37f6909bc18eb7eb; LGRID=20181220165038-52b58fa7-0434-11e9-98df-5254005c3644; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1545295840',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
    }

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        # 解析拉钩网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title",".job-name::attr(title)")
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_css("salary_min",".job_request .salary::text")
        item_loader.add_css("salary_max",".job_request .salary::text")

        item_loader.add_xpath("job_city","//*[@class='job_request']/p/span[2]/text()")
        # 经验不限设置为-1，应届设为0
        item_loader.add_xpath("work_years_min","//*[@class='job_request']/p/span[3]/text()") # 工作经验
        item_loader.add_xpath("work_years_max","//*[@class='job_request']/p/span[3]/text()") # 工作经验
        item_loader.add_css("degree_need",".job_request span:nth-child(4)::text") #学历
        item_loader.add_css("job_type",".job_request span:nth-child(5)::text") #工作类型

        item_loader.add_css("tags",".position-label li::text")
        item_loader.add_css("publish_time",".publish_time::text")
        item_loader.add_css("job_advantage",".job-advantage p::text") #职位诱惑
        item_loader.add_css("job_desc",".job_bt div") #职位描述
        item_loader.add_css("job_addr",".work_addr")
        item_loader.add_css("company_name","#job_company dt a img::attr(alt)") #公司名称
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time",datetime.now())
        # item_loader.add_css("company_url",".c_feature li:nth-child(4) a::text") # 公司网址
        job_item=item_loader.load_item()
        return job_item
