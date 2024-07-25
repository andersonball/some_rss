import requests
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# 中文 RSS 源地址
RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'  # 这里的 URL 是合法的，不需要转义

# 请求 RSS 源
response = requests.get(RSS_URL)
response.raise_for_status()  # 确保请求成功

# 解析 RSS XML
root = ET.fromstring(response.content)

def escape_xml_chars(data):
    """ 转义 XML 中的特殊字符 """
    return escape(data)

# 创建 feed.xml 文件
def create_feed(items, filename='feed.xml'):
    feed_url = 'https://andersonball.github.io/some_rss/feed.xml'  # 替换为你自己的 feed URL

    # 创建 XML 树的根节点
    rss = ET.Element('rss', version="2.0", xmlns_atom="http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = "Gooooo News Feed - 中文"
    ET.SubElement(channel, 'link').text = feed_url
    ET.SubElement(channel, 'description').text = "Google 新闻中文最新头条"
    ET.SubElement(channel, 'atom:link', href=feed_url, rel="self", type="application/rss+xml")

    for item in items:
        # 创建 item 元素
        item_element = ET.SubElement(channel, 'item')
        title = escape_xml_chars(item.find('title').text or '')
        description = escape_xml_chars(item.find('description').text or '')
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'

        ET.SubElement(item_element, 'title').text = title
        # 使用 CDATA 区域处理 description 内容
        description_cdata = f"<![CDATA[{description}]]>"
        description_element = ET.SubElement(item_element, 'description')
        description_element.text = description_cdata

        ET.SubElement(item_element, 'pubDate').text = pub_date

    # 创建 ElementTree 对象并写入文件
    tree = ET.ElementTree(rss)
    with open(filename, 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)

# 获取 RSS 频道中的项
items = root.find('channel').findall('item')
create_feed(items)

print("feed.xml 文件已生成，内容如下：")
with open('feed.xml', 'r', encoding='utf-8') as f:
    print(f.read())
