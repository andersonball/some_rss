import requests
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# 中文 RSS 源地址
RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'

def fetch_rss(url):
    """ 请求 RSS 源并解析 """
    response = requests.get(url)
    response.raise_for_status()
    return ET.fromstring(response.content)

def escape_cdata(data):
    """ 处理可能的 CDATA 区域中的特殊字符 """
    return data.replace(']]>', ']]]]><![CDATA[>')

def escape_xml_chars(data):
    """ 转义 XML 中的特殊字符 """
    return escape(data)

def create_feed(items, filename='feed.xml'):
    feed_url = 'https://andersonball.github.io/some_rss/feed.xml'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Gooooo News Feed - 中文</title>
    <link>{feed_url}</link>
    <description>Google 新闻中文最新头条</description>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml" />
""".format(feed_url=escape_xml_chars(feed_url)))
        for item in items:
            title = escape_xml_chars(item.find('title').text or '')
            link = item.find('link').text or ''
            description = item.find('description').text or ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'

            description_cdata = escape_cdata(f"<![CDATA[{description}]]>")

            file.write(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description_cdata}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
""")
        file.write("""
  </channel>
</rss>""")

def main():
    root = fetch_rss(RSS_URL)
    items = root.find('channel').findall('item')
    create_feed(items)
    print("feed.xml 文件已生成，内容如下：")
    with open('feed.xml', 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == "__main__":
    main()
