# 项目 8：Argilla 人工反馈平台

目标：创建由问题、双回答、偏好、评分、原因组成的人工反馈数据集。

```powershell
cd D:\learning\python\ai-data-engineer-portfolio\08_argilla_feedback
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:ARGILLA_API_URL="http://localhost:6900"
$env:ARGILLA_API_KEY="你的密钥"
..\.venv\Scripts\python.exe upload.py
..\.venv\Scripts\python.exe -m unittest test_upload.py
```

同名数据集默认不能重复创建；练习时可修改 `--dataset`。下一步可导出反馈，计算标注员一致性并构造偏好训练数据。

