from scrapy.cmdline import execute

import sys
import os


# 获取项目所在目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy","crawl","jobbole"])
# execute(["scrapy","crawl","zhihu"])
execute(["scrapy","crawl","lagou"])