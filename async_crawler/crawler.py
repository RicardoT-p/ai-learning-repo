"""项目1：一个遵守 robots.txt、限制域名和并发数的异步网页采集器。"""

from __future__ import annotations

import argparse
import asyncio
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser


class PageParser(HTMLParser):
    """从HTML中提取链接、可见文本和标题。

    HTMLParser 会在遇到标签或文本时调用下面的 handle_* 方法，
    因此不需要一次性把整个HTML转换成复杂的DOM树。
    """

    def __init__(self) -> None:
        super().__init__()
        # 一个页面可能有很多链接和文本片段，所以使用列表逐个收集。
        self.links: list[str] = []
        self.text: list[str] = []
        self.title: list[str] = []
        # handle_data 本身不知道文本属于哪个标签，用这个状态标记<title>范围。
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """处理形如 <a href="..."> 和 <title> 的开始标签。"""
        if tag == "a":
            # attrs是键值对列表，转成字典后更方便读取href。
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        """离开title标签后停止把普通文本记作标题。"""
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        """收集标签之间的非空文本。"""
        value = data.strip()
        if value:
            self.text.append(value)
            if self._in_title:
                self.title.append(value)


def normalize_link(base_url: str, href: str, host: str) -> str | None:
    """把相对链接转为绝对链接，并拒绝非HTTP协议和站外链接。"""
    # urljoin处理 /next、../next 等相对路径；urldefrag去掉不会改变页面的#片段。
    url = urldefrag(urljoin(base_url, href))[0]
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc == host else None


async def fetch(
    session: Any,
    url: str,
    semaphore: asyncio.Semaphore,
    retries: int = 2,
) -> str:
    """下载一个HTML页面；失败时指数退避，超过次数后把异常交给调用者。"""
    # 延迟导入让不访问网络的解析器测试即使没安装aiohttp也能运行。
    import aiohttp

    for attempt in range(retries + 1):
        try:
            # Semaphore控制同时进入网络请求区的协程数量，避免把服务器或本机压垮。
            async with semaphore, session.get(url) as response:
                if response.status == 429:
                    # 429表示请求过快。服务器给出Retry-After时优先遵守它。
                    try:
                        delay = float(response.headers.get("Retry-After", 2**attempt))
                    except ValueError:
                        # Retry-After不是简单数字时，退回到1、2、4秒的指数等待。
                        delay = 2**attempt
                    await asyncio.sleep(delay)
                    continue
                # 4xx或5xx会在这里变成异常，统一进入下面的重试逻辑。
                response.raise_for_status()
                # 本项目只处理HTML，图片、PDF等内容直接跳过。
                if "text/html" not in response.headers.get("Content-Type", ""):
                    return ""
                return await response.text(errors="replace")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if attempt == retries:
                raise
            # 第一次失败等1秒，第二次等2秒，减少连续失败带来的压力。
            await asyncio.sleep(2**attempt)
    return ""


async def load_robots(session: Any, start_url: str) -> RobotFileParser:
    """下载并解析目标网站的robots.txt规则。"""
    import aiohttp

    parsed = urlparse(start_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rules = RobotFileParser()
    try:
        async with session.get(robots_url) as response:
            # 网站没有robots.txt时允许采集；明确规则存在时按规则处理。
            text = await response.text(errors="replace") if response.status == 200 else "User-agent: *\nAllow: /"
    except (aiohttp.ClientError, asyncio.TimeoutError):
        # 无法确认规则时采取保守策略，禁止采集，避免误抓不允许的内容。
        text = "User-agent: *\nDisallow: /"
    rules.parse(text.splitlines())
    return rules


async def crawl(start_url: str, output: Path, max_pages: int, concurrency: int) -> list[dict[str, object]]:
    """从起始URL开始，广度遍历同一域名下的页面并保存结果。"""
    import aiohttp

    host = urlparse(start_url).netloc
    # Queue保存等待采集的URL；worker协程会并发消费它们。
    queue: asyncio.Queue[str] = asyncio.Queue()
    await queue.put(start_url)
    # seen既负责URL去重，也负责限制最多发现多少个页面。
    seen = {start_url}
    results: list[dict[str, object]] = []
    semaphore = asyncio.Semaphore(concurrency)
    # 单个请求最多等待20秒，防止某个网站无限期卡住整个任务。
    timeout = aiohttp.ClientTimeout(total=20)
    # 真实项目应把联系邮箱换成自己的，方便站点管理员识别和联系。
    headers = {"User-Agent": "LearningCrawler/1.0 (contact: you@example.com)"}

    # 一个ClientSession复用TCP连接，比每个URL创建一次连接更高效。
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        robots = await load_robots(session, start_url)

        async def worker() -> None:
            """不断从队列取URL，下载、解析，并把新链接放回队列。"""
            while True:
                url = await queue.get()
                try:
                    # 每个URL都检查robots规则，而不只检查起始页。
                    if not robots.can_fetch(headers["User-Agent"], url):
                        continue
                    html = await fetch(session, url, semaphore)
                    if not html:
                        continue
                    parser = PageParser()
                    parser.feed(html)
                    # 先把当前页的结构化结果保存在内存中。
                    results.append(
                        {
                            "url": url,
                            "title": " ".join(parser.title),
                            "text": " ".join(parser.text),
                        }
                    )
                    # 只把合法、同域、未见过且未超过上限的链接加入队列。
                    for href in parser.links:
                        next_url = normalize_link(url, href, host)
                        if next_url and next_url not in seen and len(seen) < max_pages:
                            seen.add(next_url)
                            await queue.put(next_url)
                except Exception as error:
                    # 单页失败不会终止整个任务；生产版应写入失败日志或重试队列。
                    print(f"失败 {url}: {error}")
                finally:
                    # 无论成功、continue还是异常都必须标记完成，否则queue.join()会永远等待。
                    queue.task_done()

        # 每个worker都是独立协程；真正的并发上限还会被Semaphore再次约束。
        workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
        # 等待队列中所有URL都被处理并调用task_done。
        await queue.join()
        # 队列清空后worker仍在无限等待新URL，因此要主动取消并回收它们。
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

    # ponytail: 小型学习任务先集中写出；数据超过内存时改为队列连接专用写入协程。
    with output.open("w", encoding="utf-8") as file:
        for item in results:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")
    return results


def main() -> None:
    """读取命令行参数，启动异步事件循环并显示最终结果。"""
    parser = argparse.ArgumentParser(description="仅采集同一域名、遵守 robots.txt 的学习爬虫")
    # url没有默认值，所以在PyCharm运行配置中也必须填写它。
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("pages.jsonl"))
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=3)
    args = parser.parse_args()
    if args.max_pages < 1 or args.concurrency < 1:
        parser.error("max-pages 和 concurrency 必须大于 0")
    # 普通同步main通过asyncio.run进入异步crawl函数。
    pages = asyncio.run(crawl(args.url, args.output, args.max_pages, args.concurrency))
    print(f"完成：{len(pages)} 页 -> {args.output}")


if __name__ == "__main__":
    # 直接运行crawler.py时执行；作为模块导入时不会自动启动爬虫。
    main()
