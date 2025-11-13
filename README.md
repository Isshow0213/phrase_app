# アプリ名 接客フレーズアプリ

このアプリは、外国語の接客フレーズを管理・再生できるWebアプリです。

## 機能一覧

- フレーズの登録・検索・削除（論理削除）
- お気に入り登録
- 音声ファイル再生
- 削除済みフレーズの復元機能
- 30日経過後の自動削除スクリプト

## 技術スタック

- Python / Flask
- MySQL
- HTML / CSS / JavaScript
- Git / GitHub

## セットアップ方法

```bash
git clone https://github.com/あなたの名前/あなたのリポジトリ名.git
cd プロジェクトフォルダ
python -m venv venv
source venv/bin/activate  # Windowsなら venv\Scripts\activate
pip install -r requirements.txt
python app.py
