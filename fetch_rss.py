import requests
import xml.etree.ElementTree as ET

# 中文 RSS 源地址
RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'

# 请求 RSS 源
response = requests.get(RSS_URL)
response.raise_for_status()  # 确保请求成功

# 解析 RSS XML
root = ET.fromstring(response.content)

# 创建 feed.xml 文件
def create_feed(items):
    with open('feed.xml', 'w', encoding='utf-8') as file:
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google News Feed - 中文</title>
    <link>https://news.google.com/</link>
    <description>Google 新闻中文最新头条</description>
    <atom:link href="https://your-username.github.io/your-repo-name/feed.xml" rel="self" type="application/rss+xml" />
""")
        for item in items:
            # 转义特殊字符
            title = escape_xml(item.find('title').text)
            link = escape_xml(item.find('link').text)
            description = escape_xml(item.find('description').text)
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'
            guid = escape_xml(item.find('link').text)

            file.write(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description}</description>
      <guid>{guid}</guid>
      <pubDate>{pub_date}</pubDate>
    </item>
""")
        file.write("""
  </channel>
</rss>""")

def escape_xml(text):
    """Escape special XML characters."""
    if text:
        text = (text.replace('&', '&amp;')
                  .replace('<', '&lt;')
                  .replace('>', '&gt;')
                  .replace('"', '&quot;')
                  .replace("'", '&apos;'))
    return text

# 获取 RSS 频道中的项
items = root.find('channel').findall('item')
create_feed(items)
