import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

def fetch_and_convert_feed():
    # 从 Google 新闻 RSS 读取
    RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
    response = requests.get(RSS_URL)
    response.raise_for_status()
    
    # 解析 RSS XML
    root = ET.fromstring(response.content)
    
    # 处理每个 item
    items = []
    for item in root.findall('channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text
        pub_date = item.find('pubDate').text

        # 提取实际链接并修改描述内容
        soup = BeautifulSoup(description, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            # 替换 Google News 相关链接
            if 'news.google.com' in url:
                real_url = convert_to_real_url(url)
                link['href'] = real_url
        
        description_modified = str(soup)
        items.append({
            'title': title,
            'link': link,
            'description': description_modified,
            'pubDate': pub_date
        })
    
    return items

def convert_to_real_url(url):
    # 在此函数中进行实际链接转换的逻辑
    # 例如，使用一些库或者API获取实际链接
    return url.replace('news.google.com', 'real-news-source.com')  # 示例替换逻辑

def create_new_feed(items, filename='new-feed.xml'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Updated News Feed</title>
    <link>https://example.com/feed</link>
    <description>Updated news feed with real links</description>
""")
        for item in items:
            file.write(f"""
    <item>
      <title>{item['title']}</title>
      <link>{item['link']}</link>
      <description><![CDATA[{item['description']}]]></description>
      <pubDate>{item['pubDate']}</pubDate>
    </item>
""")
        file.write("""
  </channel>
</rss>""")

def main():
    items = fetch_and_convert_feed()
    create_new_feed(items)

if __name__ == "__main__":
    main()
