# 项目2：Scrapy生产级采集器

## 运行

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
scrapy runspider spider.py -a start_url=https://quotes.toscrape.com
```

## 阅读顺序

1. `custom_settings`：限速、重试、缓存、断点和输出。
2. `__init__`：限定起始页和允许域名。
3. `parse`：提取数据并产生下一批请求。

Scrapy已经提供调度队列、URL去重、连接复用、重试和Feed Export，不要重复实现。

## 必做练习

1. 用 `scrapy stats` 日志记录成功数和失败数。
2. 停止程序后重新运行，观察 `.crawl-state` 的断点恢复。
3. 新增一个 Item Pipeline，丢弃正文少于50字的页面。
4. 通过 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量接入你有权使用的代理，并比较成功率、延迟与费用。

完成标准：能画出 `Scheduler → Downloader → Spider → Pipeline` 数据流。

