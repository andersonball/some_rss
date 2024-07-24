import requests
import xml.etree.ElementTree as ET

# RSS 源地址
RSS_URL = 'https://news.google.com/rss'

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
    <title>Google News Feed</title>
    <link>https://news.google.com/</link>
    <description>Latest headlines from Google News</description>
""")
        for item in items:
            # 转义特殊字符
            title = item.find('title').text
            link = item.find('link').text
            description = item.find('description').text
            description = (description.replace('&', '&amp;')
                                       .replace('<', '&lt;')
                                       .replace('>', '&gt;')
                                       .replace('"', '&quot;')
                                       .replace("'", '&apos;'))
            
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No Date'

            file.write(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
""")
        file.write("""
  </channel>
</rss>""")
