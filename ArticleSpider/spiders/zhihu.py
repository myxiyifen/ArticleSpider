# -*- coding: utf-8 -*-
import scrapy


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    # start_urls = ['https://www.zhihu.com/people/xi-yi-fen-76/activities']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    cookies = {
        '__utma': '51854390.2071314466.1542292043.1542292043.1542292043.1',
        '__utmb': '51854390.0.10.1542292043',
        '__utmc': '51854390',
        '__utmv': '51854390.100--|2=registration_date=20160201=1^3=entry_date=20160201=1',
        '__utmz': '51854390.1542292043.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/',
        '_xsrf': '"alfV7vnYKo0joZwOZ1NEOGjRbeCRsgoy"',
        '_zap': 'd19d4a99-f8e0-4f26-a35b-e7d0faf96cec',
        'capsion_ticket': '"2|1:0|10:1542292016|14:capsion_ticket|44:ZDkyNjIxZDA4ZmRjNGY0NWIzYWU5NWFiYzMwNTZiZTY=|3912c8b3b11b96c32998b326d4afc6536341c6499854e38980fcd9191b46adc9"',
        'd_c0': '"AJBhgoqlhQ6PTrpO9OtXkYGe1TDFME7CtHM=|1542267043"',
        'q_c1': '39af60c926fb49cda18f3a232e121368|1542292039000|1542292039000',
        'tgw_l7_route': '53d8274aa4a304c1aeff9b999b2aaa0a',
        'tst': 'r',
        'z_c0': '"2|1:0|10:1542292022|4:z_c0|92:Mi4xM0dPTkFnQUFBQUFBa0dHQ2lxV0ZEaVlBQUFCZ0FsVk5OdERhWEFEMnB1WEFPa3hqUTcxQjdxRTRDSnRUUnRvNzRR|54f6450ebc01c6276714e91d1686d6d56c5cb8cc0f7c019f5282b3437316e5da"',
    }

    # 重写Spider类的start_requests方法，附带Cookie值，发送POST请求
    def start_requests(self):
        # for url in self.start_urls:
        url = 'https://www.zhihu.com/inbox'
        yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.check_login)

    # 没写回调函数，自动调用parse()
    def parse(self, response):
        with open("zhihu.html", "wb") as filename:
            filename.write(response.text.encode("utf-8"))

    def parse_detail(self,response):
        pass
    # 处理响应内容
    def parse_page(self, response):
        with open("zhihu.html", "wb") as filename:
            filename.write(response.text.encode("utf-8"))

    # 此函数执行后，因为没定义回调函数callback,所以自动调用parse函数
    def check_login(self, response):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, headers=self.headers,)
        # response_text=response.text
        # print('==================')
        # print(response_text)

