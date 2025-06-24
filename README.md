# Phrase App for Multilingual Customer Support

このアプリは、外国人スタッフの接客サポートを目的としたフレーズ登録・再生ツールです。Flask + SQLite を使って構築されています。

## 🔧 機能

- よく使う日本語フレーズを登録・表示
- 多言語翻訳の表示（ネパール語など）
- 音声再生機能（generate_audio.py）
- カテゴリ別管理（例：案内・支払い・お礼）

## 🖥️ 使用技術

- Python 3.x
- Flask
- SQLite
- gTTS（Google Text-to-Speech）

## ▶️ 実行方法

```bash
pip install -r requirements.txt
python app.py
