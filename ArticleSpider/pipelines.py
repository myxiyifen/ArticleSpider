# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
# 将mysql操作变为异步化操作
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 写 保存为json文件
# class JsonWithEncodingPipeline(object):
#     # 自定义json文件的导出
#     def __init__(self):
#         self.file = codecs.open('article.json', 'w', encoding="utf-8")
#
#     # def process_item(self, item, spider):
#     #     lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
#     #     self.file.write(lines)
#     #     return item
#     def process_item(self, item, spider):
#         lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
#         self.file.write(lines)
#         return item
#
#     def spider_closed(self, spider):
#         self.file.close()


# 连接mysql数据库并插入数据
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'root', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
        insert into jobbole_article(title,url,create_date,fav_nums) 
        VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql, (item["title"], item['url'], item['create_date'], item['fav_nums']))
        self.conn.commit()


# :param str host:        host to connect
#         :param str user:        user to connect as
#         :param str password:    password to use
#         :param str passwd:      alias of password, for backward compatibility
#         :param str database:    database to use
#         :param str db:          alias of database, for backward compatibility
#         :param int port:        TCP/IP port to connect to
#         :param str unix_socket: location of unix_socket to use
#         :param dict conv:       conversion dictionary, see MySQLdb.converters
#         :param int connect_timeout:
#             number of seconds to wait before the connection attempt fails.
# 取mysql变量要跟上面的一致
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                insert into jobbole_article(title,url,create_date,fav_nums) 
                VALUES (%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (item["title"], item['url'], item['create_date'], item['fav_nums']))


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item
