import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
import re
import json
from collections import deque

class CleanCursorDocsScraper:
    def __init__(self):
        self.base_url = "https://docs.cursor.com"
        self.visited_urls = set()
        self.scraped_data = []
        self.output_dir = "cursor_docs_clean"
        self.wait_time = 1  # サーバー負荷軽減のための待機時間
        
        # 出力ディレクトリを作成
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def remove_unwanted_elements(self, soup):
        """不要な要素を除去する"""
        # 除去する要素のセレクタ
        unwanted_selectors = [
            'header', 'footer', 'nav', 'aside', 
            '.sidebar', '.navigation', '.nav', 
            'script', 'style', '.search', '.breadcrumb',
            '.header', '.footer', '[class*="nav"]', 
            '[class*="menu"]', '[class*="sidebar"]',
            '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
            '.cursor-home-page', '.search-container',
            '.page-navigation', '.table-of-contents'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        return soup
    
    def extract_clean_content(self, soup):
        """クリーンなメインコンテンツを抽出する"""
        # 不要な要素を除去
        soup = self.remove_unwanted_elements(soup)
        
        # メインコンテンツエリアを特定
        main_content = None
        selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            'article',
            '.content',
            '.documentation-content',
            '.prose',
            '.markdown-body'
        ]
        
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body') or soup
        
        return main_content
    
    def clean_text_content(self, text):
        """テキストコンテンツをクリーニングする"""
        # 不要なフレーズを除去
        unwanted_phrases = [
            'Search...', 'Ask AI', 'Sign in', 'Download', 
            'Navigation', 'Documentation', 'Guides', 
            'Website', 'Forum', 'Support', 'Was this page helpful?',
            'Yes', 'No', 'On this page', 'Cursor home page',
            'Assistant', 'Responses are generated using AI and may contain mistakes.',
            'x github website', 'Product', 'Pricing', 'Downloads',
            'Docs', 'Company', 'Careers', 'About', 'Security',
            'Privacy', 'Resources', 'Terms', 'Changelog', 'Twitter', 'GitHub'
        ]
        
        for phrase in unwanted_phrases:
            text = text.replace(phrase, '')
        
        # 連続する空白文字を単一のスペースに変換
        text = re.sub(r'\s+', ' ', text)
        # 連続する改行を最大2つまでに制限
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def extract_structured_content(self, content_element):
        """構造化されたコンテンツを抽出する"""
        sections = []
        current_section = {"title": "", "content": "", "level": 1}
        
        # 処理済みの要素を追跡
        processed_elements = set()
        
        for element in content_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'code', 'blockquote']):
            if element in processed_elements:
                continue
            
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # 新しいセクションの開始
                if current_section["title"] or current_section["content"]:
                    if current_section["content"].strip():  # 空でない場合のみ追加
                        sections.append(current_section)
                
                level = int(element.name[1])
                title = self.clean_text_content(element.get_text())
                
                # 短すぎるタイトルや記号のみのタイトルをスキップ
                if len(title) > 2 and not title.startswith('​'):
                    current_section = {
                        "title": title,
                        "level": level,
                        "content": ""
                    }
                processed_elements.add(element)
            
            elif element.name == 'p':
                text = self.clean_text_content(element.get_text())
                if len(text) > 20:  # 短すぎるテキストは除外
                    current_section["content"] += text + "\n\n"
                processed_elements.add(element)
            
            elif element.name in ['ul', 'ol']:
                # リストを整形
                list_items = []
                for li in element.find_all('li'):
                    item_text = self.clean_text_content(li.get_text())
                    if len(item_text) > 5:  # 短すぎるアイテムは除外
                        list_items.append(f"• {item_text}")
                
                if list_items:
                    current_section["content"] += "\n".join(list_items) + "\n\n"
                processed_elements.add(element)
            
            elif element.name in ['pre', 'code']:
                code_text = element.get_text().strip()
                if len(code_text) > 10:  # 短いコードスニペットは除外
                    current_section["content"] += f"```\n{code_text}\n```\n\n"
                processed_elements.add(element)
            
            elif element.name == 'blockquote':
                quote_text = self.clean_text_content(element.get_text())
                if len(quote_text) > 10:
                    current_section["content"] += f"> {quote_text}\n\n"
                processed_elements.add(element)
        
        # 最後のセクションを追加
        if current_section["title"] or current_section["content"]:
            if current_section["content"].strip():
                sections.append(current_section)
        
        # 重複を除去
        unique_sections = []
        seen_content = set()
        
        for section in sections:
            content_key = (section["title"], section["content"][:100])  # 最初の100文字で重複チェック
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_sections.append(section)
        
        return unique_sections
    
    def extract_page_info(self, soup, url):
        """ページの情報を抽出する"""
        # ページタイトルを抽出
        title = ""
        title_element = soup.find('h1') or soup.find('title')
        if title_element:
            title = self.clean_text_content(title_element.get_text())
        
        # メインコンテンツを抽出
        main_content = self.extract_clean_content(soup)
        
        if main_content:
            # 構造化されたセクションを抽出
            sections = self.extract_structured_content(main_content)
            
            return {
                'url': url,
                'title': title,
                'sections': sections
            }
        
        return None
    
    def get_page_links(self, soup, current_url):
        """ページ内のリンクを抽出する"""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(current_url, href)
            
            # Cursorドキュメントサイト内のリンクのみを対象とする
            if absolute_url.startswith(self.base_url):
                # フラグメント（#）を除去
                clean_url = absolute_url.split('#')[0]
                links.add(clean_url)
        
        return links
    
    def scrape_page(self, url):
        """単一ページをスクレイピングする"""
        print(f"スクレイピング中: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ページ情報を抽出
            page_info = self.extract_page_info(soup, url)
            
            if page_info and page_info['sections']:  # セクションが存在する場合のみ保存
                self.scraped_data.append(page_info)
                
                # クリーンな形式でファイルに保存
                filename = url.replace(self.base_url, "").replace("/", "_").strip("_")
                if not filename:
                    filename = "index"
                filename = f"{filename}.md"
                
                file_path = os.path.join(self.output_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {page_info['title']}\n\n")
                    f.write(f"**URL:** {url}\n\n")
                    f.write("---\n\n")
                    
                    for section in page_info['sections']:
                        if section['title']:
                            # 見出しレベルに応じてマークダウン形式で出力
                            level = section.get('level', 2)
                            heading_prefix = '#' * min(level + 1, 6)  # h1は既に使用済みなので+1
                            f.write(f"{heading_prefix} {section['title']}\n\n")
                        
                        if section['content'].strip():
                            f.write(f"{section['content'].strip()}\n\n")
                
                print(f"保存完了: {file_path}")
            
            # ページ内のリンクを取得
            links = self.get_page_links(soup, url)
            return links
            
        except Exception as e:
            print(f"エラー: {url} - {e}")
            return set()
    
    def scrape_docs(self, start_url=None, max_pages=100):
        """ドキュメント全体をスクレイピングする"""
        if start_url is None:
            start_url = f"{self.base_url}/welcome"
        
        urls_to_visit = deque([start_url])
        pages_scraped = 0
        
        print(f"Cursorドキュメントのスクレイピングを開始します...")
        print(f"開始URL: {start_url}")
        print(f"最大ページ数: {max_pages}")
        
        while urls_to_visit and pages_scraped < max_pages:
            current_url = urls_to_visit.popleft()
            
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            
            # ページをスクレイピング
            found_links = self.scrape_page(current_url)
            pages_scraped += 1
            
            # 新しいリンクをキューに追加
            for link in found_links:
                if link not in self.visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)
            
            # サーバー負荷軽減のための待機
            time.sleep(self.wait_time)
            
            print(f"進捗: {pages_scraped}/{max_pages} ページ完了")
        
        # 統合されたマークダウンファイルを作成
        self.create_combined_documentation()
        
        print(f"\nスクレイピング完了!")
        print(f"総ページ数: {len(self.scraped_data)}")
        print(f"出力ディレクトリ: {self.output_dir}")
    
    def create_combined_documentation(self):
        """すべてのページを統合したクリーンなドキュメントを作成"""
        combined_path = os.path.join(self.output_dir, "cursor_documentation_complete.md")
        
        with open(combined_path, "w", encoding="utf-8") as f:
            f.write("# Cursor 完全ドキュメント\n\n")
            f.write("このドキュメントは、Cursorの公式ドキュメントサイトから収集した情報をまとめたものです。\n\n")
            f.write("---\n\n")
            
            # 目次を作成
            f.write("## 目次\n\n")
            for i, page in enumerate(self.scraped_data, 1):
                f.write(f"{i}. [{page['title']}](#{self.create_anchor(page['title'])})\n")
            f.write("\n---\n\n")
            
            # 各ページの内容を追加
            for page in self.scraped_data:
                f.write(f"## {page['title']}\n\n")
                f.write(f"**URL:** {page['url']}\n\n")
                
                for section in page['sections']:
                    if section['title']:
                        f.write(f"### {section['title']}\n\n")
                    
                    if section['content'].strip():
                        f.write(f"{section['content'].strip()}\n\n")
                
                f.write("---\n\n")
        
        print(f"統合ドキュメント作成完了: {combined_path}")
    
    def create_anchor(self, text):
        """マークダウンアンカー用のテキストを作成"""
        # 特殊文字を除去し、スペースをハイフンに変換
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')

def main():
    scraper = CleanCursorDocsScraper()
    
    # スクレイピング実行
    scraper.scrape_docs(
        start_url="https://docs.cursor.com/welcome",
        max_pages=200  # 必要に応じて調整
    )

if __name__ == "__main__":
    main() 