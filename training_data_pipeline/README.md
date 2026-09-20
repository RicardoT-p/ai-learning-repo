# 项目3：大模型训练数据流水线

这个版本只用Python标准库，先理解数据流，再换DataTrove。

## 运行

```powershell
python prepare.py sample.jsonl --min-chars 20
python -m unittest -v
```

## 阅读顺序

1. `clean_text`：空白规范化和简单PII遮盖。
2. `prepare`：逐行读取、过滤、精确去重、写出。
3. `simhash`：为近似文本生成64位指纹。
4. 汉明距离：比较两个指纹不同的位数。

## 必做练习

1. 增加空文本、乱码比例和语言字段检查。
2. 为每条记录增加 `content_hash`。
3. 把过滤原因单独写入 `rejected.jsonl`。
4. 用10万条数据压测，观察O(n²)近似去重的问题。
5. 最后用DataTrove MinHash替换`simhash`列表扫描。

注意：示例正则不是完整PII识别器，真实数据还需要许可证审查、敏感信息策略和人工抽检。

