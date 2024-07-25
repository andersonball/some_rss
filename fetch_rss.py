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

def escape_cdata(data):
    """ 处理可能的 CDATA 区域中的特殊字符 """
    # 替换 CDATA 中的 "]]>" 为 "]]]]><![CDATA[>"
    return data.replace(']]>', ']]]]><![CDATA[>')

def escape_xml_chars(data):
    """ 转义 XML 中的特殊字符 """
    # 使用 xml.sax.saxutils.escape 来转义字符
    return escape(data)

# 创建 feed.xml 文件
def create_feed(items, filename='feed.xml'):
    feed_url = 'https://andersonball.github.io/some_rss/feed.xml'  # 替换为你自己的 feed URL
    with open(filename, 'w', encoding='utf-8') as file:
        # 写入 XML 头部及命名空间声明
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Gooooo News Feed - 中文</title>
    <link>{feed_url}</link>
    <description>Google 新闻中文最新头条</description>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml" />
""".format(feed_url=escape_xml_chars(feed_url)))
        for item in items:
            # 获取每个字段的内容，处理可能的缺失值
            title = escape_xml_chars(item.find('title').text or '')
            description = item.find('description').text or ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'

            # 使用 CDATA 区域包裹 description，以避免处理其中的特殊字符
            description_cdata = escape_cdata(f"<![CDATA[{description}]]>")

            # 写入每个 item，去掉 <link> 和 <guid> 标签
            file.write(f"""
    <item>
      <title>{title}</title>
      <description>{description_cdata}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
""")
        # 结束 XML 文件
        file.write("""
  </channel>
</rss>""")

# 获取 RSS 频道中的项
items = root.find('channel').findall('item')
create_feed(items)

print("feed.xml 文件已生成，内容如下：")
with open('feed.xml', 'r', encoding='utf-8') as f:
    print(f.read())
