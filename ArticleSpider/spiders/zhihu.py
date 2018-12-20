# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem

# 兼容写法python2-python3
try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    # start_urls = ['https://www.zhihu.com/people/xi-yi-fen-76/activities']
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?" \
                       "include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment" \
                       "%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail" \
                       "%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count" \
                       "%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings" \
                       "%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info" \
                       "%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized" \
                       "%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata" \
                       "%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A" \
                       "%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform" \
                       "=desktop&sort_by=default"

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

    # 入口
    # 重写Spider类的start_requests方法，附带Cookie值，发送POST请求
    def start_requests(self):
        # for url in self.start_urls:
        url = 'https://www.zhihu.com/inbox'
        yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.check_login)

    # 没写回调函数，自动调用parse()
    def parse(self, response):
        """
         提取出html页面中所有的url，并跟踪这些url进行进一步爬取
        如果提取的url中格式为/question/xxx 就下载之后直接进入解析函数
        :param response:
        :return:
        """
        all_urls = response.css("a::attr(href)").extract()
        # 给url添加主域名 https://www.zhihu.com/
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # // 过滤掉不以https开头的url
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            # print(url)
            # 利用正则表达式提取request_url和request_id
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                # print(request_url, question_id)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
                # break
            else:
                # 如果不是question Url，则对此url进行进一步跟踪，即继续解析
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面，从页面中提取出具体的question item
        if "QuestionMainAction" in response.text:
            #     处理老版本
            # 利用正则表达式提取request_url和request_id
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_css("url", response.url)
            item_loader.add_css("zhihu_id", question_id)
            question_item = item_loader.load_item()
        else:
            # 利用正则表达式提取request_url和request_id
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            # 处理新版本
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
            question_item = item_loader.load_item()
        # 解析question中的answer
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             callback=self.parse_answer)
        # 将question_item传到pipelines.py中
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        # totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item=ZhihuAnswerItem()
            answer_item["zhihu_id"]=answer["id"]
            answer_item["url"]=answer["url"]
            answer_item["question_id"]=answer["question"]["id"]
            answer_item["author_id"]=answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"]=answer["content"] if "content" in answer else None
            # 点赞数
            answer_item["praise_num"]=answer["voteup_count"]
            answer_item["comments_num"]=answer["comment_count"]
            answer_item["create_time"]=answer["created_time"]
            answer_item["update_time"]=answer["updated_time"]
            # 当前时间
            answer_item["crawl_time"]=datetime.datetime.now()
            # 提交给pipeline进一步处理
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers,
                                 callback=self.parse_answer)

    # 处理响应内容
    def parse_page(self, response):
        with open("zhihu.html", "wb") as filename:
            filename.write(response.text.encode("utf-8"))

    # 此函数执行后，因为没定义回调函数callback,所以自动调用parse函数
    def check_login(self, response):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, headers=self.headers)
            # response_text=response.text
            # print('==================')
            # print(response_text)
