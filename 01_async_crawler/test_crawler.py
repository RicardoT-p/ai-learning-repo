import unittest

from crawler import PageParser, normalize_link


class CrawlerTests(unittest.TestCase):
    """只测试纯解析逻辑，不依赖真实网络，保证测试快速且稳定。"""

    def test_parser_and_links(self) -> None:
        # 准备一小段可预测的HTML，避免外部网站变化导致测试失败。
        parser = PageParser()
        parser.feed('<title>示例</title><a href="/next#top">下一页</a>正文')

        # 验证标题和链接确实被解析出来。
        self.assertEqual(parser.title, ["示例"])
        self.assertEqual(parser.links, ["/next#top"])

        # 相对路径应转成绝对路径，并删除#top片段。
        self.assertEqual(
            normalize_link("https://example.com/a", parser.links[0], "example.com"),
            "https://example.com/next",
        )
        # 站外链接必须被拒绝，防止爬虫无边界扩散。
        self.assertIsNone(normalize_link("https://example.com", "https://other.com", "example.com"))


if __name__ == "__main__":
    unittest.main()
