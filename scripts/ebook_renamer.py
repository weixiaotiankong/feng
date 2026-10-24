#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ebook_renamer.py — 电子书批量重命名工具

将下载后的电子书（以数字 / ISBN 等无意义编号命名）按真实书名重命名。

两种用法：
1. 生成清单（便于填写书名）：
    python ebook_renamer.py --dir ./downloads --inventory
    -> 生成 ./downloads/_rename_map.csv，列：source,title（title 留空待填）

2. 按映射表重命名：
    python ebook_renamer.py --dir ./downloads --map ./downloads/_rename_map.csv
    -> 根据 csv 的 source->title 重命名文件（保留原扩展名）

支持 --dry-run 预览、--ext 限定扩展名。
"""

import argparse
import csv
import os
import sys


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符（Windows 兼容）。"""
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip().rstrip(".") or "未命名"


def build_inventory(directory: str, exts):
    """列出目录内待重命名的文件（base 名 + 空 title）。"""
    rows = []
    for fn in sorted(os.listdir(directory)):
        full = os.path.join(directory, fn)
        if not os.path.isfile(full):
            continue
        base, ext = os.path.splitext(fn)
        if exts and ext.lower() not in exts:
            continue
        rows.append((base, ""))
    return rows


def write_inventory(directory: str, rows):
    path = os.path.join(directory, "_rename_map.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "title"])
        for src, title in rows:
            w.writerow([src, title])
    print(f"已生成映射模板：{path}（请把 title 列填好真实书名，再执行 --map）")


def apply_map(directory: str, map_path: str, dry_run: bool, exts):
    mapping = {}
    with open(map_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            src = (r.get("source") or "").strip()
            title = (r.get("title") or "").strip()
            if src and title:
                mapping[src] = title
    if not mapping:
        print("映射表为空或格式不正确（需含 source,title 两列）。")
        sys.exit(1)

    done = skip = 0
    for fn in sorted(os.listdir(directory)):
        full = os.path.join(directory, fn)
        if not os.path.isfile(full):
            continue
        base, ext = os.path.splitext(fn)
        if exts and ext.lower() not in exts:
            continue
        if base in mapping:
            new_base = sanitize_filename(mapping[base])
            new_name = new_base + ext
            if new_name == fn:
                skip += 1
                continue
            new_full = os.path.join(directory, new_name)
            if os.path.exists(new_full):
                print(f"[跳过] 目标已存在：{new_name}")
                skip += 1
                continue
            if dry_run:
                print(f"[预览] {fn} -> {new_name}")
            else:
                os.rename(full, new_full)
                print(f"[重命名] {fn} -> {new_name}")
            done += 1
    print(f"完成：重命名 {done}，跳过 {skip}"
          + ("（dry-run，未实际修改）" if dry_run else ""))


def main():
    ap = argparse.ArgumentParser(description="电子书批量重命名工具")
    ap.add_argument("--dir", required=True, help="电子书所在目录")
    ap.add_argument("--inventory", action="store_true",
                    help="生成待填书名的映射模板 CSV")
    ap.add_argument("--map", help="应用映射表 CSV 进行重命名")
    ap.add_argument("--ext", nargs="*", help="限定处理的扩展名，如 .pdf .epub")
    ap.add_argument("--dry-run", action="store_true", help="只预览不修改")
    args = ap.parse_args()

    exts = [e.lower() if e.startswith(".") else "." + e.lower()
            for e in (args.ext or [])]
    if not os.path.isdir(args.dir):
        print(f"目录不存在：{args.dir}")
        sys.exit(1)

    if args.inventory:
        rows = build_inventory(args.dir, exts)
        write_inventory(args.dir, rows)
        return
    if args.map:
        apply_map(args.dir, args.map, args.dry_run, exts)
        return
    print("请指定 --inventory（生成模板）或 --map（应用重命名）。")


if __name__ == "__main__":
    main()
