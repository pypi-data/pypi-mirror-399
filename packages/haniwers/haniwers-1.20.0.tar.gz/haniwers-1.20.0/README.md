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

## インストール方法

### 推奨：pipx を使用

```bash
# 基本インストール（DAQ + データ処理 + 解析）
pipx install haniwers

# オプション：閾値可視化（hvplot）
pipx install "haniwers[analysis]"

# オプション：Notebook分析（plotly, altair）
pipx install "haniwers[viz]"

# 全機能
pipx install "haniwers[all]"

# 動作確認
haniwers --help
```

### 詳細ドキュメント

- **[ユーザーガイド](https://haniwers.readthedocs.io/ja/latest/users/)** - インストール方法、セットアップ、使い方
- **[トラブルシューティング](https://haniwers.readthedocs.io/ja/latest/users/faq.html)** - よくある質問

## 基本的な使い方

```bash
# バージョン確認
$ haniwers version

# シリアルポート確認
$ haniwers port list
$ haniwers port test /dev/ttyUSB0

# データ取得（DAQ）
$ haniwers daq --config daq.toml

# データ処理・変換
$ haniwers preprocess input.raw output.csv

# 閾値スキャン
$ haniwers scan --config scan.toml

# 閾値フィッティング
$ haniwers fit data.csv
```

詳細は各コマンドのヘルプを確認：

```bash
haniwers daq --help
haniwers scan --help
```

---

# 開発者向け：開発に参加する

## 開発環境セットアップ

### 環境構築（推奨方法）

```bash
# 1. リポジトリをクローン
git clone https://gitlab.com/qumasan/haniwers.git
cd haniwers

# 2. 開発環境をセットアップ（Poetry）
poetry install

# 3. テスト実行
task test

# 4. コード品質チェック
task format:check
task lint:fix

# 5. CLIを試す
poetry run haniwers --help
```


### よく使うコマンド

```bash
# テストを実行
task test

# コードをフォーマット・チェック
task format
task lint:fix

# ドキュメントをプレビュー
task livehtml

# 詳細は以下で確認
task --list
```

### 詳細リソース

- **[CLAUDE.md](./CLAUDE.md)** - AI開発ガイド（環境構築、アーキテクチャ、ワークフロー）
- **[プロジェクト憲法](/.specify/memory/constitution.md)** - 開発原則・テスト基準
- **[公式ドキュメント](https://haniwers.readthedocs.io/)** - APIリファレンス・ユーザーガイド

---

# リンク

- **[公式ドキュメント](https://haniwers.readthedocs.io/)**
- **[解析ログブック](https://qumasan.gitlab.io/haniwers/)**
- **[このリポジトリ](https://gitlab.com/qumasan/haniwers/)**
