# 项目1：异步网页采集器

## 第一步：安装

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 第二步：先运行测试

```powershell
python -m unittest -v
```

## 第三步：采集练习网站

```powershell
python crawler.py https://quotes.toscrape.com --max-pages 10 --concurrency 3
```

结果写入 `pages.jsonl`，每行是一条 JSON，程序中断也不会产生半条记录。

## 第四步：按调用顺序阅读

1. `main()`：解析命令行参数。
2. `crawl()`：创建队列、会话和 worker。
3. `worker()`：消费 URL、解析页面、发现新链接。
4. `fetch()`：并发限制、429处理、超时与重试。
5. `PageParser`：从HTML提取标题、文本和链接。

## 必做练习

1. 把 `concurrency` 改成 1、3、10，记录运行时间和失败率。
2. 给输出增加 `fetched_at` 字段。
3. 增加 `--delay` 参数，在每次请求前等待。
4. 将失败 URL 写入 `failures.jsonl`。

完成标准：能解释为什么 `queue.task_done()` 必须放在 `finally` 中。

