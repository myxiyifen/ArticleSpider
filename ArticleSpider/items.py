# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value + "-jobble"


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    #     去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


# 什么都不做
def return_value(value):
    return value


# 重载ItemLoader类
class ArticleItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        # output_processor=TakeFirst() #取create_date list中的第一个值
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # 覆盖掉 default_output_processor = TakeFirst()
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    # def get_insert_sql(self):
    #     insert_sql = """
    #             insert into jobbole_article(title,url,create_date,fav_nums)
    #             VALUES (%s,%s,%s,%s)
    #             """
    #     params = (self["title"], self['url'], self['create_date'], self['fav_nums'])
    #     return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    #         知乎问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
                   insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
                     watch_user_num, click_num, crawl_time
                     )
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                   ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
                    watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
               """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num(("".join(self["answer_num"])).replace(',', ''))
        comments_num = extract_num(("".join(self["comments_num"])).replace(',', ''))

        if len(self["watch_user_num"]) == 2:
            # if "," in self["watch_user_num"][0]:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            # if "," in self["watch_user_num"][1]:
            click_num = int(self["watch_user_num"][1].replace(',', ''))
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params

        # # 插入知乎question表的sql语句
        # insert_sql = """
        #     insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,
        #     watch_user_num,click_num,crwal_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        # """
        # # 将list转换为string
        # zhihu_id = self["zhihu_id"][0]
        # topics = ",".join(self["topics"])
        # url = "".join(self["url"])
        # title = "".join(self["title"])
        # content = "".join(self["content"])
        # answer_num = extract_num("".join(self["answer_num"]))
        # comments_num = extract_num("".join(self["comments_num"]))
        # # watch_user_num = extract_num("".join(self["watch_user_num"]))
        # if len(self["watch_user_num"]) == 2:
        #     watch_user_num = int(self["watch_user_num"][0])
        #     click_num = int(self["watch_user_num"][1])
        # else:
        #     watch_user_num = int(self["watch_user_num"][0])
        #     click_num = 0
        # # click_num = extract_num("".join(self["click_num"]))
        # crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        #
        # params = (
        # zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        #
        # return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    #     知乎问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()  # 点赞数
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎answer表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
                  update_time=VALUES(update_time)
              """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql, params


def remove_splash(value):
    value = value.replace("/", "")
    return value


def split_salary_min(value):
    value = value.split("-")[0].replace("k", "000")
    return int(value)


def split_salary_max(value):
    value = value.split("-")[1].replace("k", "000")
    return int(value)


def work_years_min(value):
    if value == "经验应届毕业生 /":
        value = int(0)
    elif value == "经验不限 /":
        value = int(-1)
    else:
        match_re = re.match(".*?(\d+)-(\d+).*?", value)
        value = int(match_re.group(1))
    return value


def work_years_max(value):
    if value == "经验应届毕业生 /":
        value = int(0)
    elif value == "经验不限 /":
        value = int(-1)
    elif value == "经验10年以上 /":
        value == int(20)
    else:
        match_re = re.match(".*?(\d+)-(\d+).*?", value)
        value = int(match_re.group(2))
    return value


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary_min = scrapy.Field(
        input_processor=MapCompose(split_salary_min)
    )
    salary_max = scrapy.Field(
        input_processor=MapCompose(split_salary_max)
    )
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years_min = scrapy.Field(
        input_processor=MapCompose(work_years_min)
    )
    work_years_max = scrapy.Field(
        input_processor=MapCompose(work_years_max)
    )
    degree_need = scrapy.Field()
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
    )
    job_addr = scrapy.Field(
        # 可以执行多个函数，从左到右依次执行
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary_min, salary_max, job_city, work_years_min, work_years_max, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min), salary_max=VALUES(salary_max)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary_min"], self["salary_max"], self["job_city"],
            self["work_years_min"], self["work_years_max"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["tags"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params
