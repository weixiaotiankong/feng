# feng

> 司法鉴定资料与脚本 · 电子书管理项目

## 简介

本仓库用于归集两类内容：

1. **司法鉴定资料与脚本** —— 伤残鉴定等标准的条款研读、参考资料与辅助处理脚本。
2. **电子书管理** —— 批量采集、整理与重命名的工具脚本。
   - 基于 Python（`requests` + `BeautifulSoup`）多线程抓取；
   - 采集到的电子书统一按真实书名命名、本地归档。
   - 实际电子书文件保存在本地，**不纳入本仓库**；本仓库只放脚本、索引与配置。

## 目录结构

```
feng/
├── scripts/
│   ├── ebook_downloader.py   # 电子书批量下载（requests + BeautifulSoup + 多线程）
│   └── ebook_renamer.py      # 电子书按真实书名批量重命名
├── references/
│   ├── README.md                                       # 本目录说明
│   └── 人体损伤致残程度分级_4.4_胸部损伤研读.md          # 司法鉴定条款研读笔记
├── .github/workflows/
│   └── ci.yml               # GitHub Actions（Python 3.13 CI）
├── requirements.txt         # Python 依赖
├── .gitignore
├── LICENSE
└── README.md
```

## 环境要求

- Python 3.13+
- 依赖见 `requirements.txt`（`requests`、`beautifulsoup4`）

```bash
pip install -r requirements.txt
```

## 电子书管理脚本

### 批量下载 `scripts/ebook_downloader.py`

```bash
# 从链接列表文件下载（每行一个 URL）
python scripts/ebook_downloader.py --url-file urls.txt --out ./downloads

# 直接指定若干链接
python scripts/ebook_downloader.py --url https://x/book1.pdf https://x/book2.epub
```

- 若 URL 是直接文件链接（.pdf/.epub 等）则直接下载；若是网页则用 BeautifulSoup 解析页面内电子书链接。
- 多线程并发（默认 8 线程），支持超时、重试、跳过已存在文件（`--overwrite` 可覆盖）。

### 批量重命名 `scripts/ebook_renamer.py`

电子书常以数字 / ISBN 命名，本脚本按真实书名重命名：

```bash
# 1) 先生成待填书名的映射模板
python scripts/ebook_renamer.py --dir ./downloads --inventory
#   -> 生成 ./downloads/_rename_map.csv（source,title 两列，title 留空待填）

# 2) 在 CSV 里填好真实书名后，执行重命名
python scripts/ebook_renamer.py --dir ./downloads --map ./downloads/_rename_map.csv
#   加 --dry-run 可先预览，不实际改名
```

## 司法鉴定资料

- `references/人体损伤致残程度分级_4.4_胸部损伤研读.md`：《人体损伤致残程度分级》四级伤残（颈部及胸部损伤，含肺移植、呼吸困难、肺切除等）研读笔记。**以官方发布文本为准。**

## 自动化（CI）

每次 push / PR 到 `main` 时，GitHub Actions 会：

1. 检出代码
2. 安装 Python 3.13
3. 安装 `requirements.txt` 中的依赖
4. 对所有 Python 文件做语法编译检查
5. 若存在 `tests/` 目录则运行 pytest

## 许可证

[MIT](./LICENSE)
