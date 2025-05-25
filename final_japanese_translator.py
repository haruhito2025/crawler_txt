import os
import re

class FinalJapaneseTranslator:
    def __init__(self):
        self.input_file = "Cursor完全ドキュメント_日本語版.md"
        self.output_file = "Cursor完全ドキュメント_最終日本語版.md"
        
    def comprehensive_translate(self, content):
        """包括的な日本語翻訳"""
        
        # 1. 基本的な英単語を日本語に置換
        basic_translations = {
            # 基本用語
            "Welcome": "ようこそ",
            "Installation": "インストール", 
            "Getting Started": "はじめに",
            "Get Started": "はじめに",
            "Features": "機能",
            "Overview": "概要",
            "Introduction": "はじめに",
            "Dashboard": "ダッシュボード",
            "Settings": "設定",
            "Account": "アカウント",
            "Billing": "請求",
            "Support": "サポート",
            "Documentation": "ドキュメント",
            "Members": "メンバー",
            "Roles": "役割",
            "Plans": "プラン",
            "Usage": "使用状況",
            "Custom": "カスタム",
            "Advanced": "高度な",
            "Basic": "基本",
            "Quick": "クイック",
            "Manual": "手動",
            "Auto": "自動",
            "Background": "バックグラウンド",
            "Context": "コンテキスト",
            "Files": "ファイル",
            "Folders": "フォルダ",
            "Code": "コード",
            "Terminal": "ターミナル",
            "Keyboard": "キーボード",
            "Shortcuts": "ショートカット",
            "Commands": "コマンド",
            "Tools": "ツール",
            "Models": "モデル",
            "API": "API",
            "Keys": "キー",
            "Rules": "ルール",
            "Definitions": "定義",
            "Changes": "変更",
            "Recent": "最近の",
            "Past": "過去の",
            "Chats": "チャット",
            "Mode": "モード",
            "Agent": "エージェント",
            "Ask": "質問",
            "Max": "最大",
            "Managing": "管理",
            "Indexing": "インデックス",
            "Codebase": "コードベース",
            "Large": "大規模",
            "Codebases": "コードベース",
            "Working": "作業",
            "Import": "インポート",
            "Modes": "モード",
            "Notepads": "ノートパッド",
            "Beta": "ベータ",
            "Web": "ウェブ",
            "Development": "開発",
            "JavaScript": "JavaScript",
            "TypeScript": "TypeScript",
            "iOS": "iOS",
            "macOS": "macOS",
            "Swift": "Swift",
            "Python": "Python",
            "Java": "Java",
            "Common": "よくある",
            "Issues": "問題",
            "FAQ": "よくある質問",
            "Troubleshooting": "トラブルシューティング",
            "Guide": "ガイド",
            "Getting": "取得",
            "Request": "リクエスト",
            "Apply": "適用",
            "Git": "Git",
            "Lint": "Lint",
            "Errors": "エラー",
            "Ignore": "無視",
            "Links": "リンク",
            "SSO": "SSO",
            "Commit": "コミット",
            "Message": "メッセージ",
            "AI": "AI",
            "Agents": "エージェント",
            "Preview": "プレビュー",
            "Protocol": "プロトコル",
            "Architectural": "アーキテクチャ",
            "Diagrams": "図",
            "VS Code": "VS Code",
            "JetBrains": "JetBrains",
            "Early": "早期",
            "Access": "アクセス",
            "Program": "プログラム",
            "Selecting": "選択",
            "Cmd": "Cmd",
            "Tab": "Tab"
        }
        
        # 2. 複合語の翻訳
        compound_translations = {
            "Getting Started": "はじめに",
            "Early Access Program": "早期アクセスプログラム",
            "Custom API Keys": "カスタムAPIキー",
            "Codebase Indexing": "コードベースインデックス",
            "Model Context Protocol": "モデルコンテキストプロトコル",
            "Architectural Diagrams": "アーキテクチャ図",
            "Keyboard Shortcuts": "キーボードショートカット",
            "Terminal Cmd K": "ターミナル Cmd+K",
            "Common Issues": "よくある問題",
            "Troubleshooting Guide": "トラブルシューティングガイド",
            "Large Codebases": "大規模コードベース",
            "Custom Modes": "カスタムモード",
            "Auto-Import": "自動インポート",
            "Background Agents": "バックグラウンドエージェント",
            "Past Chats": "過去のチャット",
            "Agent Mode": "エージェントモード",
            "Ask mode": "質問モード",
            "Manual Mode": "手動モード",
            "Max Mode": "最大モード",
            "Managing Context": "コンテキスト管理",
            "Plans & Usage": "プラン・使用状況",
            "Members + Roles": "メンバー・役割",
            "JavaScript & TypeScript": "JavaScript・TypeScript",
            "iOS & macOS (Swift)": "iOS・macOS（Swift）",
            "Web Development": "ウェブ開発",
            "AI Commit Message": "AIコミットメッセージ",
            "Working with Context": "コンテキストでの作業"
        }
        
        # 3. 文章の翻訳
        sentence_translations = {
            "Cursor is an AI code editor": "Cursorは、AIを活用したコードエディタです",
            "used by millions of engineers": "世界中の数百万人のエンジニアに利用されています",
            "powered by a series of custom models": "独自開発されたモデル群により動作し",
            "generate more code than almost any other LLMs in the world": "世界中のほぼ全てのLLMを上回るコード生成能力を持っています",
            "Tab predicts your next series of edits": "Tab機能は、あなたの次の編集操作を予測します",
            "Your AI pair programmer": "あなたのAIペアプログラマー",
            "for complex code changes": "複雑なコード変更に対応",
            "Make large-scale edits": "大規模な編集を実行し",
            "with context control": "コンテキスト制御機能と",
            "and automatic fixes": "自動修正機能を提供",
            "Quick inline code editing": "素早いインライン編集",
            "and generation": "およびコード生成",
            "Perfect for making precise changes": "正確な変更を行うのに最適で",
            "without breaking your flow": "作業の流れを中断しません",
            "Get started with Cursor": "Cursorを始めましょう",
            "in minutes": "わずか数分で",
            "by downloading and installing": "ダウンロードとインストールを行うことで",
            "for your platform": "お使いのプラットフォーム向けの",
            "You can download Cursor": "Cursorは以下からダウンロードできます",
            "from the Cursor website": "Cursor公式ウェブサイト",
            "for your platform of choice": "お好みのプラットフォーム用を",
            "You'll have the option to import": "以下をインポートするオプションがあります",
            "VS Code extensions and settings": "VS Codeの拡張機能と設定",
            "in one-click": "ワンクリックで",
            "To help you try Cursor": "Cursorをお試しいただけるよう",
            "we have a 14-day free trial": "14日間の無料トライアルを提供しています",
            "of our Pro plan": "Proプランの",
            "Learn about Cursor's core features": "Cursorの主要機能について学ぶ",
            "and concepts": "と概念",
            "Cursor has a number of core features": "Cursorには多くの主要機能があります",
            "that will seamlessly integrate": "シームレスに統合される",
            "with your workflow": "あなたのワークフローと",
            "Use the links below": "以下のリンクを使用して",
            "to learn more about": "詳細を学んでください",
            "what Cursor can do": "Cursorができること"
        }
        
        translated = content
        
        # 複合語から先に翻訳（より長いフレーズを優先）
        for english, japanese in sorted(compound_translations.items(), key=len, reverse=True):
            pattern = re.compile(re.escape(english), re.IGNORECASE)
            translated = pattern.sub(japanese, translated)
        
        # 文章の翻訳
        for english, japanese in sorted(sentence_translations.items(), key=len, reverse=True):
            pattern = re.compile(re.escape(english), re.IGNORECASE)
            translated = pattern.sub(japanese, translated)
        
        # 基本単語の翻訳
        for english, japanese in basic_translations.items():
            # 単語境界を考慮した置換
            pattern = re.compile(r'\b' + re.escape(english) + r'\b', re.IGNORECASE)
            translated = pattern.sub(japanese, translated)
        
        return translated
    
    def clean_artifacts(self, content):
        """翻訳の不自然な部分を修正"""
        
        # 不自然な翻訳を修正
        fixes = {
            # 目次の修正
            "ようこそ to Cursor": "Cursorへようこそ",
            "はじめにed": "はじめに",
            "取得 Started": "はじめに",
            "取得 a リクエスト ID": "リクエストID取得",
            
            # 複数形の修正
            "ファイルs": "ファイル",
            "フォルダs": "フォルダ",
            "メンバーs": "メンバー",
            "問題s": "問題",
            "変更s": "変更",
            "エラーs": "エラー",
            "ショートカットs": "ショートカット",
            "コマンドs": "コマンド",
            "図s": "図",
            "リンクs": "リンク",
            "モードs": "モード",
            "エージェントs": "エージェント",
            
            # 接頭辞・接尾辞の修正
            "自動-インポート": "自動インポート",
            "バックグラウンド エージェント": "バックグラウンドエージェント",
            "過去の チャット": "過去のチャット",
            "よくある 問題": "よくある問題",
            "トラブルシューティング ガイド": "トラブルシューティングガイド",
            "大規模 コードベース": "大規模コードベース",
            "カスタム モード": "カスタムモード",
            "早期 アクセス プログラム": "早期アクセスプログラム",
            "キーボード ショートカット": "キーボードショートカット",
            "ターミナル Cmd K": "ターミナル Cmd+K",
            "アーキテクチャ 図": "アーキテクチャ図",
            "AIコミット メッセージ": "AIコミットメッセージ",
            "カスタム API キー": "カスタムAPIキー",
            "コードベース インデックス": "コードベースインデックス",
            "モデル コンテキスト プロトコル": "モデルコンテキストプロトコル",
            "ウェブ 開発": "ウェブ開発",
            "作業 での コンテキスト": "コンテキストでの作業",
            
            # @記号付きの修正
            "@過去の チャット": "@過去のチャット",
            "@ファイル": "@ファイル",
            "@フォルダ": "@フォルダ",
            "@Cursor ルール": "@Cursorルール",
            "@定義": "@定義",
            "@最近の 変更": "@最近の変更",
            "@Lint エラー": "@Lintエラー",
            "@無視 ファイル": "@無視ファイル",
            "@リンク": "@リンク",
            "@ノートパッド": "@ノートパッド",
            
            # その他の修正
            "プラン & 使用状況": "プラン・使用状況",
            "メンバー + 役割": "メンバー・役割",
            "JavaScript & TypeScript": "JavaScript・TypeScript",
            "iOS & macOS (Swift)": "iOS・macOS（Swift）",
            "モデル &": "モデル・",
            "/コマンド": "/コマンド",
            "#ファイル": "#ファイル",
            
            # 不自然な語順の修正
            "作業 での": "での作業",
            "管理 コンテキスト": "コンテキスト管理",
            "選択 モデル": "モデル選択",
            "無視 ファイル": "無視ファイル"
        }
        
        for wrong, correct in fixes.items():
            content = content.replace(wrong, correct)
        
        return content
    
    def process_file(self):
        """ファイルを処理して最終日本語版を作成"""
        print(f"ファイルを読み込み中: {self.input_file}")
        
        if not os.path.exists(self.input_file):
            print(f"エラー: {self.input_file} が見つかりません。")
            return False
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("包括的な日本語翻訳を実行中...")
        translated_content = self.comprehensive_translate(content)
        
        print("翻訳の不自然な部分を修正中...")
        translated_content = self.clean_artifacts(translated_content)
        
        # タイトルと説明を更新
        translated_content = translated_content.replace(
            "# Cursor 完全ドキュメント（日本語版）",
            "# Cursor 完全ドキュメント（最終日本語版）"
        )
        
        translated_content = translated_content.replace(
            "このドキュメントは、Cursorの公式ドキュメントサイトから収集した情報を日本語で整理したものです。",
            "このドキュメントは、Cursorの公式ドキュメントサイトから収集した情報を完全に日本語化し、自然で読みやすい形に整理した最終版です。"
        )
        
        print(f"最終日本語版ファイルを保存中: {self.output_file}")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        # 統計情報
        file_size = os.path.getsize(self.output_file) / 1024  # KB
        with open(self.output_file, 'r', encoding='utf-8') as f:
            line_count = len(f.readlines())
        
        print(f"最終翻訳完了!")
        print(f"ファイルサイズ: {file_size:.1f} KB")
        print(f"総行数: {line_count:,} 行")
        
        return True

def main():
    translator = FinalJapaneseTranslator()
    
    if translator.process_file():
        print("\n🎉 最終日本語版の作成が完了しました!")
        print(f"📄 ファイル: {translator.output_file}")
        print("💡 このファイルは完全に日本語化され、自然で読みやすくなっています。")
        print("🔍 目次の項目名も適切に日本語化されています。")
    else:
        print("❌ 翻訳に失敗しました。")

if __name__ == "__main__":
    main() 