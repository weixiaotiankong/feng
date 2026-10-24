# 项目仓库

> 这是一个由 WorkBuddy 初始化并链接到 GitHub 的项目仓库。

## 简介

（请在此补充项目的实际说明：背景、目标、技术栈等。）

当前仓库已包含以下基础设施：

- `.gitignore` —— 忽略本地状态、依赖、密钥等不应入库的文件
- `LICENSE` —— 开源许可证（默认 MIT，可按需修改）
- `.github/workflows/ci.yml` —— GitHub Actions 持续集成流程

## 目录结构

```
.
├── .github/
│   └── workflows/
│       └── ci.yml        # 自动构建 / 校验流程
├── .gitignore            # 忽略规则
├── LICENSE               # 许可证
└── README.md             # 本文件
```

## 本地开发

```bash
# 克隆（首次）
git clone <你的仓库地址>
cd <仓库目录>

# 日常提交
git add .
git commit -m "描述你的改动"
git push origin main
```

## CI

推送到 `main` 分支或发起 Pull Request 时，GitHub Actions 会自动：

1. 检出代码
2. 安装 Python 3.13
3. 安装 `requirements.txt` 中的依赖（若存在）
4. 对所有 Python 文件做语法编译检查
5. 若存在 `tests/` 目录则运行 pytest

## 许可证

见 [LICENSE](./LICENSE)（MIT）。
