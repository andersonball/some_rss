import requests
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# 中文 RSS 源地址
RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'

# 请求 RSS 源
response = requests.get(RSS_URL)
response.raise_for_status()  # 确保请求成功

# 解析 RSS XML
root = ET.fromstring(response.content)

# 创建 feed.xml 文件
def create_feed(items, filename='feed.xml'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Goooo News Feed - 中文</title>
    <link>https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans</link>
    <description>Google 新闻中文最新头条</description>
    <atom:link href="https://andersonball.github.io/some_rss/feed.xml" rel="self" type="application/rss+xml" />
""")
        for item in items:
            title = escape(item.find('title').text or '')
            link = escape(item.find('link').text or '')
            description = escape(item.find('description').text or '')
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'
            guid = escape(item.find('link').text or '')

            file.write(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description><![CDATA[{description}]]></description>
      <pubDate>{pub_date}</pubDate>
      <guid>{guid}</guid>
    </item>
""")
        file.write("""
  </channel>
</rss>""")

# 获取 RSS 频道中的项
items = root.find('channel').findall('item')
create_feed(items)
