#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 轉 Markdown 轉換腳本 (v2)

此腳本會讀取一個 HTML 檔案，將其內容轉換為 Markdown，
並將結果儲存在同一目錄下，同時會清理輸出檔名中的特殊字元。

用法:
    python convert_html_to_md.py {FILENAME.HTML}

範例:
    python convert_html_to_md.py "我的[文章] (1).html"
    
    ... 將會讀取 "我的[文章] (1).html"
    ... 並儲存為 "我的-文章-1.md"

依賴:
    - beautifulsoup4 (請使用 'pip install beautifulsoup4' 安裝)
"""

import sys
import os
import re

# 檢查 'beautifulsoup4' 函式庫是否已安裝
try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    print("錯誤: 'beautifulsoup4' 函式庫未找到。", file=sys.stderr)
    print("請使用 'pip install beautifulsoup4' 來安裝。", file=sys.stderr)
    sys.exit(1)

def html_to_markdown(html_content: str) -> str:
    """
    將特定的 HTML 文章內容轉換為 Markdown 格式。
    (此函數基於先前請求的 HTML 結構)

    參數:
        html_content (str): 包含 HTML 內容的字串。

    返回:
        str: 轉換後的 Markdown 內容字串。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_parts = []

    # 1. 提取標題
    title_tag = soup.select_one('.article-title')
    if title_tag:
        markdown_parts.append(f"# {title_tag.get_text(strip=True)}")

    # 2. 提取作者和日期資訊
    info_parts = []
    author_tag = soup.select_one('.article-info .course-title')
    if author_tag:
        info_parts.append(f"**{ author_tag.get_text(strip=True)}** ")
    
    date_tag = soup.select_one('.article-info .article-publish-time')
    if date_tag:
        info_parts.append(f" **{date_tag.get_text(strip=True)}** ")
    
    if info_parts:
        markdown_parts.append("\n".join(info_parts))

    # 3. 提取封面圖片
    cover_img_tag = soup.select_one('.article-cover-wrap img')
    if cover_img_tag and cover_img_tag.get('src'):
        markdown_parts.append(f"![Article Cover]( {cover_img_tag.get('src')} )")

    # 4. 處理文章正文內容
    body_container = soup.select_one('.editor-show')
    if body_container:
        for element in body_container.find_all(recursive=False):
            if element.name == 'p':
                # --- 優化後的邏輯 ---
                line_parts = []
                for child in element.children:
                    if isinstance(child, NavigableString):
                        # 將所有空白(換行,tab,多個空格)替換為單一空格
                        text = re.sub(r'\s+', ' ', str(child))
                        line_parts.append(text)
                    elif child.name in ('b', 'strong'):
                        # 粗體標籤內部的文字直接 strip 處理
                        text = child.get_text(strip=True)
                        if text:
                            line_parts.append(f" **{text}** ")
                
                # 組合所有部分
                full_line = "".join(line_parts)
                # 再清理一次組合後可能產生的多餘空格
                cleaned_line = re.sub(r' +', ' ', full_line).strip()
                
                if cleaned_line:
                    markdown_parts.append(cleaned_line)
                # --- 邏輯結束 ---
            
            elif element.name == 'figure':
                img_tag = element.find('img')
                if img_tag and img_tag.get('src'):
                    markdown_parts.append(f"![Image]( {img_tag.get('src')} )")
            
            elif element.name == 'div' and 'split' in element.get('class', []):
                markdown_parts.append("---")
            
            else:
                pass

    return '\n\n'.join(markdown_parts)

def sanitize_filename(name: str) -> str:
    """
    清理檔名，移除特殊字元，並用連字符替換空格。

    參數:
        name (str): 原始檔名 (不含副檔名)。

    返回:
        str: 清理後的檔名。
    """
    # 1. 將空格或底線替換為連字符
    name = re.sub(r'[\s_]+', '-', name)
    
    # 2. 移除所有非 (英文字母, 數字, 連字符) 的字元
    #    (保留中文字元)
    #    移除 [ ] ( ) ! @ # $ % ^ & * 等符號
    name = re.sub(r'[^\w\s-]', '', name, flags=re.U)
    
    # 3. 將多個連續的連字符合併為一個
    name = re.sub(r'-+', '-', name)
    
    # 4. 移除開頭和結尾的連字符
    name = name.strip('-')
    
    # 5. 如果檔名為空，提供一個預設值
    if not name:
        name = 'converted-article'
        
    return name

def main():
    """
    主執行函數
    """
    # 1. 檢查參數
    if len(sys.argv) != 2:
        print(f"用法: python {os.path.basename(__file__)} <FILENAME.HTML>", file=sys.stderr)
        print("範例: python convert_html_to_md.py \"my article.html\"", file=sys.stderr)
        sys.exit(1)

    input_filepath = sys.argv[1]

    # 2. 檢查輸入檔案是否存在
    if not os.path.isfile(input_filepath):
        print(f"錯誤: 檔案未找到 -> {input_filepath}", file=sys.stderr)
        sys.exit(1)

    # 3. 處理路徑和檔名
    directory = os.path.dirname(input_filepath) or '.'
    filename = os.path.basename(input_filepath)
    base_name = os.path.splitext(filename)[0]

    # 4. 清理檔名
    fixed_base_name = sanitize_filename(base_name)
    output_filepath = os.path.join(directory, f"{fixed_base_name}.md")

    print(f"--- 處理開始 ---")
    print(f"  輸入檔案: {input_filepath}")
    print(f"  輸出檔案: {output_filepath}")

    # 5. 讀取檔案
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"\n錯誤: 無法讀取檔案 {input_filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    # 6. 執行轉換
    try:
        markdown_output = html_to_markdown(html_content)
    except Exception as e:
        print(f"\n錯誤: HTML 轉換失敗: {e}", file=sys.stderr)
        sys.exit(1)

    # 7. 寫入檔案
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
    except Exception as e:
        print(f"\n錯誤: 無法寫入檔案 {output_filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"--- 處理完成 ---")

# --- 腳本執行入口 ---
if __name__ == "__main__":
    main()