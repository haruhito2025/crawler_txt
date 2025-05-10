#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
テキストファイルの重複排除と統合を行うスクリプト
入力: scraped_text/ ディレクトリ内のテキストファイル
出力: unique_combined_text.txt
"""

import os
import sys
from typing import Set, List
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 定数
SCRAPED_DIR = "scraped_text"
OUTPUT_FILE = "unique_combined_text.txt"
ENCODINGS = ['utf-8', 'shift_jis', 'cp932']  # 試行するエンコーディングのリスト
VIDEO_EXTENSIONS = ['.mp4.txt', '.mov.txt', '.avi.txt','_mp4.txt', '_mov.txt', '_avi.txt']  # 除外する動画ファイルの拡張子

def setup_output_file() -> bool:
    """出力ファイルの準備を行う"""
    try:
        # 出力ディレクトリの作成
        output_dir = os.path.dirname(OUTPUT_FILE)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"出力ディレクトリ {output_dir} を作成しました")

        # 既存ファイルの削除
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
            logger.info(f"既存のファイル {OUTPUT_FILE} を削除しました")
        return True
    except Exception as e:
        logger.error(f"出力ファイルの準備中にエラーが発生しました: {e}")
        return False

def read_text_file(file_path: str) -> Set[str]:
    """テキストファイルを読み込み、ユニークな行のセットを返す"""
    unique_lines = set()
    
    for encoding in ENCODINGS:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line:  # 空行は無視
                        unique_lines.add(stripped_line)
            logger.info(f"{file_path} を {encoding} で読み込みました")
            return unique_lines
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"ファイル読み込み中にエラーが発生しました {file_path}: {e}")
            return unique_lines
    
    logger.warning(f"{file_path} をどのエンコーディングでも読み込めませんでした")
    return unique_lines

def process_files() -> Set[str]:
    """全てのテキストファイルを処理し、ユニークな行のセットを返す"""
    all_unique_lines = set()
    
    if not os.path.exists(SCRAPED_DIR):
        logger.error(f"ディレクトリ {SCRAPED_DIR} が見つかりません")
        return all_unique_lines

    logger.info(f"ディレクトリ {SCRAPED_DIR} からテキストファイルを読み込んでいます...")
    
    for filename in os.listdir(SCRAPED_DIR):
        # 動画ファイルのテキストファイルを除外
        if filename.endswith(".txt") and not any(video_ext in filename.lower() for video_ext in VIDEO_EXTENSIONS):
            file_path = os.path.join(SCRAPED_DIR, filename)
            unique_lines = read_text_file(file_path)
            all_unique_lines.update(unique_lines)
    
    return all_unique_lines

def write_output_file(unique_lines: Set[str]) -> bool:
    """ユニークな行を出力ファイルに書き込む"""
    try:
        sorted_lines = sorted(list(unique_lines))
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for line in sorted_lines:
                f.write(line + "\n")
        logger.info(f"ユニークな行 {len(sorted_lines)} 件を {OUTPUT_FILE} に保存しました")
        return True
    except Exception as e:
        logger.error(f"ファイル書き込みエラーが発生しました: {e}")
        return False

def main():
    """メイン処理"""
    if not setup_output_file():
        sys.exit(1)
    
    unique_lines = process_files()
    if not unique_lines:
        logger.error("処理可能なテキストファイルが見つかりませんでした")
        sys.exit(1)
    
    if not write_output_file(unique_lines):
        sys.exit(1)
    
    logger.info("処理が完了しました")

if __name__ == "__main__":
    main() 