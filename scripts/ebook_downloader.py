#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ebook_downloader.py — 电子书批量下载工具

基于 requests + BeautifulSoup + 多线程（ThreadPoolExecutor）实现批量下载。
适用于从书库网页批量抓取 PDF / EPUB 等电子书文件。

用法示例：
    # 从 urls.txt（每行一个链接）下载到 ./downloads
    python ebook_downloader.py --url-file urls.txt --out ./downloads

    # 直接传入若干 URL
    python ebook_downloader.py --url https://x/book1.pdf https://x/book2.epub

说明：
    - 若 URL 直接指向 .pdf/.epub 等文件则直接下载；
    - 若 URL 是网页，则用 BeautifulSoup 解析页面内所有电子书直链并下载；
    - 多线程并发，默认 8 线程；已存在的文件默认跳过（--overwrite 可覆盖）。
"""

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}
EBOOK_EXTS = (".pdf", ".epub", ".mobi", ".azw3", ".djvu")


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符（Windows 兼容）。"""
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip().rstrip(".") or "未命名"


def collect_links_from_page(url: str, session: requests.Session, timeout: int):
    """解析网页，返回页面内所有电子书直链。"""
    try:
        resp = session.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"[解析失败] {url}: {e}")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for tag in soup.find_all(["a", "link"]):
        href = tag.get("href")
        if not href:
            continue
        full = urljoin(url, href)
        if full.lower().endswith(EBOOK_EXTS):
            links.append(full)
    return links


def download_one(url: str, out_dir: str, session: requests.Session,
                 timeout: int, overwrite: bool, retries: int):
    """下载单个文件，返回 (url, ok, msg)。"""
    parsed = urlparse(url)
    base = os.path.basename(parsed.path)
    if not base or "." not in base:
        base = sanitize_filename(url) + ".bin"
    filename = sanitize_filename(base)
    path = os.path.join(out_dir, filename)
    if os.path.exists(path) and not overwrite:
        return (url, True, "已存在，跳过")
    for attempt in range(1, retries + 1):
        try:
            with session.get(url, headers=DEFAULT_HEADERS,
                             timeout=timeout, stream=True) as r:
                r.raise_for_status()
                os.makedirs(out_dir, exist_ok=True)
                with open(path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            size = os.path.getsize(path)
            return (url, True, f"下载完成 ({size} bytes)")
        except Exception as e:  # noqa: BLE001
            if attempt == retries:
                return (url, False, f"失败: {e}")
            time.sleep(2 * attempt)
    return (url, False, "未知错误")


def main():
    ap = argparse.ArgumentParser(description="电子书批量下载工具")
    ap.add_argument("--url-file", help="包含下载链接的文本文件，每行一个")
    ap.add_argument("--url", nargs="*", help="直接指定的下载链接")
    ap.add_argument("--out", default="./downloads", help="输出目录（默认 ./downloads）")
    ap.add_argument("--workers", type=int, default=8, help="并发线程数（默认 8）")
    ap.add_argument("--timeout", type=int, default=30, help="请求超时秒数")
    ap.add_argument("--retries", type=int, default=3, help="失败重试次数")
    ap.add_argument("--overwrite", action="store_true", help="覆盖已存在文件")
    args = ap.parse_args()

    urls = []
    if args.url_file:
        with open(args.url_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    if args.url:
        urls.extend(args.url)
    if not urls:
        print("未提供任何下载链接。使用 --url-file 或 --url。")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)
    session = requests.Session()

    # 网页类链接展开为直链
    direct_urls = []
    for u in urls:
        if u.lower().endswith(EBOOK_EXTS):
            direct_urls.append(u)
        else:
            direct_urls.extend(collect_links_from_page(u, session, args.timeout))

    # 去重
    seen, final = set(), []
    for u in direct_urls:
        if u not in seen:
            seen.add(u)
            final.append(u)

    print(f"待下载：{len(final)} 个文件")

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [
            ex.submit(download_one, u, args.out, session,
                      args.timeout, args.overwrite, args.retries)
            for u in final
        ]
        for fut in as_completed(futures):
            url, success, msg = fut.result()
            if success:
                ok += 1
                print(f"[OK] {url} -> {msg}")
            else:
                fail += 1
                print(f"[FAIL] {url} -> {msg}")
    print(f"完成：成功 {ok}，失败 {fail}，输出目录 {args.out}")


if __name__ == "__main__":
    main()
