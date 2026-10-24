# feng

> 司法鉴定资料与脚本 · 电子书管理项目

## 简介

本仓库用于归集两类内容：

1. **司法鉴定资料与脚本** —— 伤残鉴定等标准的条款研读、参考资料与辅助处理脚本。
2. **电子书管理** —— 批量采集、整理与重命名的工具脚本。
   - 基于 Python（`requests` + `BeautifulSoup`）多线程抓取；
   - 采集到的电子书统一按真实书名命名、本地归档。
   - 实际电子书文件保存在本地，**不纳入本仓库**；本仓库只放脚本、索引与配置。

> 说明：当前为初始化骨架，具体的脚本与资料目录将逐步补充。

## 目录结构（建议）

```
feng/
├── scripts/            # Python 工具脚本（电子书抓取、重命名等）
├── references/         # 司法鉴定参考资料、条款研读笔记
├── docs/               # 文档与说明
├── .github/workflows/  # CI（见下）
├── .gitignore
├── LICENSE
└── README.md
```

## 环境要求

- Python 3.13+
- 依赖见 `requirements.txt`（如 `requests`、`beautifulsoup4`）

## 本地使用

```bash
# 安装依赖
pip install -r requirements.txt

# 运行示例脚本（文件名按实际调整）
python scripts/xxx.py
```

## 自动化（CI）

每次 push / PR 到 `main` 时，GitHub Actions 会：

1. 检出代码
2. 安装 Python 3.13
3. 安装 `requirements.txt` 中的依赖（若存在）
4. 对所有 Python 文件做语法编译检查
5. 若存在 `tests/` 目录则运行 pytest

## 许可证

[MIT](./LICENSE)
