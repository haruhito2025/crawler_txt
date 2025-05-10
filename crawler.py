import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque
import os
import re

# クロール設定
# START_URL = "https://" # コードから直接指定する START_URL は削除またはコメントアウト
# DOMAIN = urlparse(START_URL).netloc # DOMAIN の決定方法も変更が必要

MAX_DEPTH = 2 # リンクを辿る最大の深さ
WAIT_TIME = 1 # 各ページ取得間の待機時間（秒）。サーバー負荷軽減のため必須！
OUTPUT_DIR = "scraped_text" # 抽出したテキストを保存するディレクトリ
# ROBOTS_TXT_URL = f"https://{DOMAIN}/robots.txt" # DOMAIN が決まってから設定

# --- 追加: URLリストファイルのパス ---
URL_LIST_FILE = "urls.txt" # ここでURLリストファイルのパスを指定します

# 既に訪れたURLを記録するためのセット
visited_urls = set()
# 探索待ちのURLとその深さを格納するキュー
urls_to_visit = deque() # 初期状態では空のキューを作成

# robots.txt の Disallow ルールを格納するリスト
disallowed_paths_by_domain = {} # ドメインごとに Disallow ルールを格納するように変更

# 出力ディレクトリを作成
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 修正: URLリストファイルからURLを読み込む ---
print(f"Loading URLs from {URL_LIST_FILE}...")
initial_urls = []
try:
    with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 空行やコメント行を無視
            if line and not line.startswith("#"):
                initial_urls.append(line)
except FileNotFoundError:
    print(f"エラー: URLリストファイル '{URL_LIST_FILE}' が見つかりません。ファイルを作成してください。")
    exit() # ファイルが見つからなければプログラムを終了
except Exception as e:
    print(f"エラー: URLリストファイルの読み込み中にエラーが発生しました: {e}")
    exit() # 読み込みエラーが発生したらプログラムを終了

if not initial_urls:
    print(f"エラー: URLリストファイル '{URL_LIST_FILE}' に有効なURLが含まれていません。URLを記述してください。")
    exit() # 有効なURLがなければプログラムを終了

# 初期URLをキューに追加し、対応するドメインの robots.txt ルールをロードする
domains_to_load_robots_txt = set()
for url in initial_urls:
    urls_to_visit.append((url, 0))
    try:
        domain = urlparse(url).netloc
        if domain:
            domains_to_load_robots_txt.add(domain)
    except Exception as e:
        print(f"Warning: Could not parse domain from URL {url}: {e}")


"""# --- robots.txt をドメインごとに読み込む ---
print("Loading robots.txt for relevant domains...")
for domain in domains_to_load_robots_txt:
    robots_txt_url = f"https://{domain}/robots.txt"
    print(f"Attempting to load robots.txt from {robots_txt_url}...")
    disallowed_paths = load_robots_txt(robots_txt_url)
    disallowed_paths_by_domain[domain] = disallowed_paths
    if disallowed_paths:
        print(f"Disallowed paths found for {domain}:")
        for path in disallowed_paths:
            print(f"- {path}")
    else:
        print(f"No Disallow rules found in robots.txt for {domain} or failed to load.")
"""

def load_robots_txt(robots_url):
    """robots.txt ファイルを読み込み、Disallow ルールを取得する"""
    rules = []
    try:
        response = requests.get(robots_url, timeout=5)
        response.raise_for_status()
        # UTF-8でデコードできない場合は他のエンコーディングも試す
        try:
            content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = response.content.decode('shift_jis')
            except Exception:
                 content = response.text # requests に自動判定させる

        for line in content.splitlines():
            line = line.strip()
            # Allow ディレクティブも考慮する場合はここにロジックを追加する必要がありますが、
            # シンプルな Disallow 回避のためにここでは Disallow のみ見ます。
            if line.lower().startswith("disallow:"):
                path = line[len("disallow:"):].strip()
                if path:
                    # robots.txt のパスパターンを正規表現に変換 (簡易的なもの)
                    # * は任意の文字列、$ は行末にマッチ
                    # エスケープしてから置換
                    path_pattern = re.escape(path).replace('\\*', '.*').replace('\\$', '$')
                    rules.append(path_pattern)
        return rules
    except requests.exceptions.RequestException as e:
        # print(f"Warning: Could not fetch robots.txt from {robots_url}: {e}") # メッセージは上で出力済み
        return [] # 取得できない場合はルールなしとして続行 (倫理的にはアクセスすべきでない)
    except Exception as e:
        # print(f"Warning: Error processing robots.txt from {robots_url}: {e}") # メッセージは上で出力済み
        return []

# --- robots.txt をドメインごとに読み込む ---
print("Loading robots.txt for relevant domains...")
for domain in domains_to_load_robots_txt:
    robots_txt_url = f"https://{domain}/robots.txt"
    print(f"Attempting to load robots.txt from {robots_txt_url}...")
    disallowed_paths = load_robots_txt(robots_txt_url)
    disallowed_paths_by_domain[domain] = disallowed_paths
    if disallowed_paths:
        print(f"Disallowed paths found for {domain}:")
        for path in disallowed_paths:
            print(f"- {path}")
    else:
        print(f"No Disallow rules found in robots.txt for {domain} or failed to load.")


def is_allowed_by_robots_txt(url, disallowed_rules_by_domain):
    """URLが robots.txt のルールで許可されているかチェックする"""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_with_query = parsed_url.path + (f"?{parsed_url.query}" if parsed_url.query else "")
        if path_with_query == "":
             path_with_query = "/"

        # そのドメインの robots.txt ルールを取得
        disallowed_rules = disallowed_rules_by_domain.get(domain, [])

        for pattern in disallowed_rules:
            if re.match(pattern, path_with_query):
                return False # 禁止されているパスにマッチした場合
        return True # 禁止されていない場合
    except Exception as e:
        print(f"Error checking robots.txt for {url}: {e}")
        return True # チェック中にエラーが発生した場合は、安全のため許可するとする


def is_same_domain(url, target_domain):
    """URLが指定したドメインと同一かチェックする"""
    try:
        # スキーム (http/https) とネットロケーション (ドメイン名+ポート) で比較
        return urlparse(url).netloc == target_domain
    except Exception as e:
        # print(f"Error parsing URL {url}: {e}") # 必要であればデバッグ用にコメントアウト解除
        return False


def scrape_and_find_links(url, depth):
    """
    指定されたURLのページをスクレイピングし、テキストとリンクを抽出する。
    """

    print(f"Depth {depth}: Scraping {url}")
    visited_urls.add(url) # 訪れたURLとして記録

    text_content = ""
    links = []
    current_domain = urlparse(url).netloc


    try:
        # ページのHTMLを取得
        response = requests.get(url, timeout=10) # タイムアウト設定
        response.raise_for_status() # 200以外のステータスコードで例外発生

        # HTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 不要な要素の削除 ---
        # 対象サイトのHTML構造に合わせて、適切なセレクタを指定してください
        # 例: ヘッダー、フッター、ナビゲーション、サイドバーなどを削除
        # 開発者ツールでHTML構造を確認し、削除したい要素のタグ名、id、classなどを特定してください。
        # nip-ltd.co.jp やその他のサイトに合わせて、ここを編集してください。
        # 前回のコードにあった重複ブロックは削除済みです。
        selectors_to_remove = ['header', 'footer', 'nav', 'aside', '.sidebar', '#header', '#footer', '#nav']

        for selector in selectors_to_remove:
            for element in soup.select(selector):
                element.extract() # 要素を削除

        # script, style要素などを除外
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        # --- テキストの抽出 ---
        # シンプルに、不要要素削除後のページの全てのテキストを抽出する場合
        text_content = soup.get_text(separator='\n', strip=True)

        # --- 抽出したテキストのクレンジング（オプション）---
        # 例: 連続する3つ以上の改行を1つにする
        text_content = re.sub(r'\n{3,}', '\n\n', text_content)


        # テキストをファイルに保存
        # ファイル名はURLから安全な文字を使って生成
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_").replace(":", "_").replace(".", "_")
        filename = filename[:200] + ".txt" # 長すぎるファイル名を制限 (ファイルシステムによってはさらに短い方が良い場合も)
        file_path = os.path.join(OUTPUT_DIR, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\n\n")
                f.write(text_content)
            print(f"Saved text to {file_path}")
        except Exception as e:
             print(f"Error saving file {file_path}: {e}")


        # ページ内のリンクを抽出
        if depth < MAX_DEPTH:
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href']) # 相対URLを絶対URLに変換
                # URLのフラグメント(#...)を除去して重複を避ける
                parsed_absolute_url = urlparse(absolute_url)
                # クエリパラメータは残すかどうかの方針による。ここでは残す。
                clean_url = parsed_absolute_url.scheme + "://" + parsed_absolute_url.netloc + parsed_absolute_url.path + (f"?{parsed_absolute_url.query}" if parsed_absolute_url.query else "")


                # 同一ドメイン内で、かつ robots.txt で許可されており、まだ探索待ち/訪れていないURLをリストに追加
                # キューに追加する前に重複チェックとrobots.txtチェック、ドメインチェックを行う
                # チェック済みのURLをvisited_urlsに追加するのは、キューから取り出した後に行う
                # ここでは、単にリンク候補としてリストに追加する
                links.append(clean_url)


    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

    return text_content, links # 抽出したテキストとリンクを返す（ここではテキストはファイルに保存済みなので、主にリンクが重要）

"""""
# --- クロール実行部分 ---
print("Starting crawl...")
processed_urls_queue = set() # キューに追加済みのURLを記録するためのセット（重複追加防止）

# 初期URLをキューに追加
for url, depth in urls_to_visit:
    # 初期URLリストの中に重複やrobots.txtで禁止されているものがある可能性も考慮
    parsed_initial_url = urlparse(url)
    initial_domain = parsed_initial_url.netloc
    if initial_domain and \
       is_same_domain(url, initial_domain) and \
       is_allowed_by_robots_txt(url, disallowed_paths_by_domain) and \
       url not in visited_urls and \
       url not in processed_urls_queue: # キューにまだ追加されていないかチェック
        urls_to_visit.append((url, depth))
        processed_urls_queue.add(url) # キューに追加したURLを記録
    else:
         print(f"Skipping initial URL {url} (invalid, disallowed, or duplicate)")


while urls_to_visit:
    current_url, current_depth = urls_to_visit.popleft() # キューからURLを取り出す

    # 既に訪れた URL はスキップ（キューから取り出した時点で最終チェック）
    if current_url in visited_urls:
        print(f"Skipping {current_url} (already visited)")
        continue

    # 最大深さを超えている場合はスキップ
    if current_depth > MAX_DEPTH:
         print(f"Skipping {current_url} (depth exceeded)")
         visited_urls.add(current_url) # 訪れてはいないが、今後訪れる必要はないのでvisitedに追加
         continue

    # ページをスクレイピングし、リンクを取得
    # 抽出されたテキストは関数内でファイル保存される
    _, found_links = scrape_and_find_links(current_url, current_depth)

    # 見つかったリンクをキューに追加（最大深さまで）
    if current_depth < MAX_DEPTH:
        current_domain = urlparse(current_url).netloc
        for link in found_links:
            # リンク先のドメインが現在のドメインと同一かチェック
            # robots.txt で許可されているかチェック
            # 既に訪れたことがあるか、キューに既に入っているかチェック
            if is_same_domain(link, current_domain) and \
               is_allowed_by_robots_txt(link, disallowed_paths_by_domain) and \
               link not in visited_urls and \
               link not in processed_urls_queue: # キューにまだ追加されていないかチェック
                 urls_to_visit.append((link, current_depth + 1))
                 processed_urls_queue.add(link) # キューに追加したURLを記録


    # サーバーに負荷をかけないために待機
    time.sleep(WAIT_TIME)

print("Crawling finished.")"""
# ... (前略：インポート、設定、関数定義など) ...

# --- クロール実行部分 ---
print("Starting crawl...")
processed_urls_queue = set() # キューに追加済みのURLを記録するためのセット（重複追加防止）

# 初期URLをキューに追加
initial_urls_with_depth = [(url, 0) for url in initial_urls] # 初期URLリストに深さ0を追加
initial_urls = [] # initial_urls はもう使用しないので空にするか、この行自体削除しても良い

for url, depth in initial_urls_with_depth: # 初期URLリストを処理
    # 初期URLリストの中に重複やrobots.txtで禁止されているものがある可能性も考慮
    parsed_initial_url = urlparse(url)
    initial_domain = parsed_initial_url.netloc
    if initial_domain and \
       is_same_domain(url, initial_domain) and \
       is_allowed_by_robots_txt(url, disallowed_paths_by_domain) and \
       url not in visited_urls and \
       url not in processed_urls_queue: # キューにまだ追加されていないかチェック
        urls_to_visit.append((url, depth))
        processed_urls_queue.add(url) # キューに追加したURLを記録
    else:
         print(f"Skipping initial URL {url} (invalid, disallowed, or duplicate)")


# --- 修正: クロール実行ループ ---
# キューの長さが0より大きい間ループ
while len(urls_to_visit) > 0:
    current_url, current_depth = urls_to_visit.popleft() # キューからURLを取り出す

    # 既に訪れた URL はスキップ（キューから取り出した時点で最終チェック）
    if current_url in visited_urls:
        print(f"Skipping {current_url} (already visited)")
        continue

    # 最大深さを超えている場合はスキップ
    if current_depth > MAX_DEPTH:
         print(f"Skipping {current_url} (depth exceeded)")
         visited_urls.add(current_url) # 訪れてはいないが、今後訪れる必要はないのでvisitedに追加
         continue

    # ページをスクレイピングし、リンクを取得
    # 抽出されたテキストは関数内でファイル保存される
    _, found_links = scrape_and_find_links(current_url, current_depth)

    # 見つかったリンクをキューに追加（最大深さまで）
    if current_depth < MAX_DEPTH:
        # 現在処理しているURLのドメインを取得
        current_domain = urlparse(current_url).netloc
        for link in found_links:
            # リンク先のドメインが現在のドメインと同一かチェック
            # robots.txt で許可されているかチェック
            # 既に訪れたことがあるか、キューに既に入っているかチェック
            if is_same_domain(link, current_domain) and \
               is_allowed_by_robots_txt(link, disallowed_paths_by_domain) and \
               link not in visited_urls and \
               link not in processed_urls_queue: # キューにまだ追加されていないかチェック
                 urls_to_visit.append((link, current_depth + 1))
                 processed_urls_queue.add(link) # キューに追加したURLを記録


    # サーバーに負荷をかけないために待機
    time.sleep(WAIT_TIME)

print("Crawling finished.")

# ... (後略：重複排除・統合のコードなど) ...