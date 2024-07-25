import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

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

        # 使用 BeautifulSoup 解析 description
        soup = BeautifulSoup(description, 'html.parser')
        
        # 生成修改后的描述
        description_modified = str(soup)
        
        items.append({
            'title': title,
            'link': link,
            'description': description_modified,
            'pubDate': pub_date
        })
    
    return items

def create_new_feed(items, filename='feed.xml'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Some_RSS</title>
    <link>https://example.com/feed</link>
    <description>Updated news feed with original links</description>
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
