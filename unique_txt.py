import os
from bs4 import BeautifulSoup # 前回のスクレイピングコードからBeautifulSoupが必要になる場合があるのでインポートしておく
from urllib.parse import urljoin, urlparse # 同上
import requests # 同上
import time # 同上
from collections import deque # 同上

# --- ここから重複排除・統合のコード ---

# スクリーピングしたテキストファイルが保存されているディレクトリ
SCRAPED_DIR = "scraped_text"
# 重複を除外したテキストを保存するファイル
OUTPUT_FILE = "unique_combined_text.txt"

# 全てのユニークな行を格納するセット
unique_lines = set()

# 出力ファイルのディレクトリが存在するか確認し、なければ作成
output_dir = os.path.dirname(OUTPUT_FILE)
if output_dir and not os.path.exists(output_dir): # output_dirが空文字列でない（ディレクトリが指定されている）かつ存在しない場合
    try:
        os.makedirs(output_dir)
        print(f"出力ディレクトリ {output_dir} を作成しました。")
    except Exception as e:
        print(f"出力ディレクトリ {output_dir} の作成に失敗しました: {e}")
        # ディレクトリ作成失敗は致命的なので、ここで処理を中断することも検討できますが、
        # シンプルにするため、このまま進みます（ただし書き込みは失敗する可能性が高い）。

# 出力ファイルが存在すれば削除
if os.path.exists(OUTPUT_FILE):
    try:
        os.remove(OUTPUT_FILE)
        print(f"既存のファイル {OUTPUT_FILE} を削除しました。")
    except Exception as e:
        print(f"既存ファイル {OUTPUT_FILE} の削除に失敗しました: {e}")
        # 削除に失敗した場合、新しい内容が既存ファイルに追記される可能性があります。
        # 注意が必要です。

# スクレイピングしたテキストディレクトリ内のファイルを一つずつ処理
print(f"ディレクトリ {SCRAPED_DIR} からテキストファイルを読み込んでいます...")
if not os.path.exists(SCRAPED_DIR):
    print(f"エラー: ディレクトリ {SCRAPED_DIR} が見つかりません。スクレイピングを実行してから再度お試しください。")
else:
    for filename in os.listdir(SCRAPED_DIR):
        # 動画ファイルのテキストファイルを除外
        if filename.endswith(".txt") and not any(video_ext in filename.lower() for video_ext in ['.mp4.txt', '_mp4.txt',  '.mov.txt', '_mov.txt',  '.avi.txt', '_avi.txt']):
            file_path = os.path.join(SCRAPED_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    # ファイルの各行を読み込み、前後の空白を除去してセットに追加
                    for line in f:
                        stripped_line = line.strip()
                        if stripped_line: # 空行は無視
                            unique_lines.add(stripped_line)
            except UnicodeDecodeError:
                print(f"エンコーディングエラー: {file_path} をUTF-8で読み込めません。他のエンコーディングを試みます...")
                try:
                    # 他のエンコーディングで試してみる (例: shift_jis)
                    with open(file_path, "r", encoding="shift_jis") as f:
                        for line in f:
                            stripped_line = line.strip()
                            if stripped_line:
                                unique_lines.add(stripped_line)
                    print(f"{file_path} をShift_JISで読み込みました。")
                except Exception as e:
                    print(f"代替エンコーディングでも読み込めませんでした: {file_path}: {e}")
            except Exception as e:
                print(f"ファイル読み込み中にエラーが発生しました {file_path}: {e}")

# ユニークな行を結合して新しいファイルに書き出す
print(f"ユニークな行 {len(unique_lines)} 件をファイルに書き込んでいます...")
try:
    # セットは順序を保持しないため、必要であればソートなどを挟む
    # アルファベット順にソートして書き出し
    sorted_unique_lines = sorted(list(unique_lines))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in sorted_unique_lines:
            f.write(line + "\n")
    print(f"ユニークな行を {OUTPUT_FILE} に保存しました")
except Exception as e:
    print(f"ファイル書き込みエラーが発生しました: {e}")