"""项目2：用Scrapy内置调度、去重、限速和导出能力实现同域爬虫。"""

from urllib.parse import urlparse

import scrapy


class PortfolioSpider(scrapy.Spider):
    """提取页面标题和正文，并继续跟踪同一域名下的链接。"""

    # name是Scrapy识别和启动Spider时使用的唯一名称。
    name = "portfolio"

    # 设置直接写在Spider里，方便这个单文件教学项目独立运行。
    custom_settings = {
        # 尊重目标网站robots.txt中的允许和禁止规则。
        "ROBOTSTXT_OBEY": True,
        # 每个域名最多同时发送4个请求，并在请求之间保留基础延迟。
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "DOWNLOAD_DELAY": 0.5,
        # 根据服务器响应速度自动调整请求频率。
        "AUTOTHROTTLE_ENABLED": True,
        # 临时网络错误最多额外重试2次。
        "RETRY_TIMES": 2,
        # 开启本地HTTP缓存，重复调试时减少对网站的请求。
        "HTTPCACHE_ENABLED": True,
        # 保存调度队列和去重状态，使中断后可以继续运行。
        "JOBDIR": ".crawl-state",
        "USER_AGENT": "LearningScrapyBot/1.0 (contact: you@example.com)",
        # Scrapy负责把yield的数据逐行写成UTF-8 JSONL。
        "FEEDS": {"items.jsonl": {"format": "jsonlines", "encoding": "utf8", "overwrite": True}},
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, start_url: str = "https://quotes.toscrape.com", **kwargs: object) -> None:
        """接受命令行的-a start_url参数，并据此限制允许访问的域名。"""
        super().__init__(**kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).hostname or ""]

    def parse(self, response: scrapy.http.Response):
        """解析一个响应；yield字典给导出器，yield Request给调度器。"""
        # CSS选择器提取标题和body中的全部文本节点。
        yield {
            "url": response.url,
            "title": response.css("title::text").get(default="").strip(),
            "text": " ".join(response.css("body *::text").getall()).strip(),
        }

        # 找出页面里的每个链接，相对路径由response.urljoin补全。
        for href in response.css("a::attr(href)").getall():
            url = response.urljoin(href)
            # 双重检查域名；重复URL会由Scrapy自带去重器自动忽略。
            if urlparse(url).hostname in self.allowed_domains:
                # 下载完成后仍交给当前parse方法，形成持续爬取循环。
                yield response.follow(url, callback=self.parse)
