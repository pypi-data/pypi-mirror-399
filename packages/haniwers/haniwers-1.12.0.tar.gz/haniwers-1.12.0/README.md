![GitLab Tag](https://img.shields.io/gitlab/v/tag/qumasan%2Fhaniwers?sort=semver&style=for-the-badge) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/haniwers?style=for-the-badge) ![GitLab License](https://img.shields.io/gitlab/license/qumasan%2Fhaniwers?style=for-the-badge)
![Gitlab Pipeline Status](https://img.shields.io/gitlab/pipeline-status/qumasan%2Fhaniwers?style=for-the-badge) ![GitLab Last Commit](https://img.shields.io/gitlab/last-commit/qumasan%2Fhaniwers?style=for-the-badge)

---

# Haniwers : ハニワーズ

墳Qの解析コード（個人用）

![w:300](./docs/_static/haniwer.png)

## 概要

宇宙線検出器OSECHIでデータを取得・解析するPythonツール。

- ✅ データ取得（DAQ）
- ✅ データ処理・解析
- ✅ スレッショルド測定

---

# ユーザー向け：インストール

## PyPiからインストール

### 基本インストール（DAQ + データ処理 + 閾値フィッティング）

```bash
$ pipx install haniwers
$ haniwers --help
```

### オプション機能

**閾値フィッティングの可視化**（hvplot使用）:
```bash
$ pipx install "haniwers[analysis]"
```

**Notebook分析**（plotly, altair等）:
```bash
$ pipx install "haniwers[viz]"
```

**全機能**:
```bash
$ pipx install "haniwers[all]"
```

## コマンド例

```bash
$ haniwers version           # バージョン確認
$ haniwers daq --help        # データ取得
$ haniwers scan              # 閾値測定
$ haniwers fit               # 閾値計算
```

詳細は `haniwers docs` でオンラインヘルプを確認できます。

---

# 開発者向け：開発に参加する

## クイックスタート

```bash
# 1. リポジトリをクローン
$ git clone https://gitlab.com/qumasan/haniwers.git
$ cd haniwers

# 2. Docker イメージをビルド（初回のみ）
$ docker compose build base

# 3. テストを実行
$ docker compose run --rm test

# 4. CLI コマンドを実行
$ docker compose run --rm cli haniwers --help
```

## ブランチ運用

| ブランチ | 用途 |
|---------|------|
| **main** | 最新の安定版 |
| **v1** | 新機能開発（推奨） |
| **v0** | ドキュメント修正のみ |

## 詳細ドキュメント

- **[開発者ガイド](docs/developers/index.md)**：環境構築、ブランチ管理、貢献方法
- **[Dockerガイド](docs/developers/containers.md)**：Dockerを使った開発環境
- **[公式ドキュメント](https://haniwers.readthedocs.io/)**：APIリファレンス

---

# リンク

- **[公式ドキュメント](https://haniwers.readthedocs.io/)**
- **[解析ログブック](https://qumasan.gitlab.io/haniwers/)**
- **[このリポジトリ](https://gitlab.com/qumasan/haniwers/)**
