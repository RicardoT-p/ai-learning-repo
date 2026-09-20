# 项目4：LLM反馈与回归评测

## 第一步：建立人工反馈库

```powershell
python feedback.py add --prompt "解释asyncio" --response "asyncio用于协作式并发" --rating 4 --tags python
python feedback.py list
python feedback.py export
```

## 第二步：运行固定评测集

```powershell
python evaluate.py cases.jsonl
python -m unittest -v
```

## 阅读顺序

1. `feedback.py/connect`：SQLite建表。
2. `feedback.py/main`：参数化写入、查看、导出。
3. `token_f1`：回答与参考答案的词元重合度。
4. `evaluate`：比较基线模型和候选模型，找出退化案例。

## 必做练习

1. 给反馈增加 `model_name` 和 `model_version`。
2. 将低于3分的记录导出为错误案例集。
3. 增加延迟和调用成本字段。
4. 将模型调用结果自动追加到 `cases.jsonl`。
5. 数据量和协作需求出现后，再接入Argilla、DeepEval和Phoenix。

这里的Token F1只是确定性教学指标，不能替代事实性、安全性和人工评审。

