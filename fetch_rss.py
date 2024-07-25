import requests
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup

# 中文 RSS 源地址
RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'

def escape_xml_chars(data):
    """ 转义 XML 中的特殊字符 """
    return escape(data)

def extract_actual_link_from_google(url):
    """ 从 Google News 链接中提取实际的新闻源链接 """
    try:
        # 访问 Google News 链接并获取最终的重定向地址
        response = requests.get(url, allow_redirects=True)
        # 返回最终重定向的 URL
        return response.url
    except requests.RequestException as e:
        print(f"请求链接失败: {e}")
        return url  # 如果出现错误，返回原始链接

def extract_actual_link(description):
    """ 从 description 中提取 Google News 链接并转换为实际的新闻源链接 """
    soup = BeautifulSoup(description, 'lxml')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href and href.startswith('https://news.google.com/'):
            return extract_actual_link_from_google(href)
    return ''  # 如果没有找到 Google News 链接，返回空字符串

def create_feed(items, filename='feed.xml'):
    """ 创建 feed.xml 文件 """
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
            link = item.find('link').text or ''
            description = item.find('description').text or ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'

            # 尝试从 description 中提取实际新闻链接
            actual_link = extract_actual_link(description)
            if actual_link:
                link = actual_link  # 替换为实际的新闻链接

            # 处理描述中的特殊字符（可能包含 HTML 标记）
            description = escape_xml_chars(description)

            # 写入每个 item
            file.write(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
    </item>
""")
        
        # 结束 XML 文件
        file.write("""
  </channel>
</rss>""")

try:
    # 请求 RSS 源
    response = requests.get(RSS_URL)
    response.raise_for_status()  # 确保请求成功

    # 解析 RSS XML
    root = ET.fromstring(response.content)

    # 获取 RSS 频道中的项
    items = root.find('channel').findall('item')
    create_feed(items)

    print("feed.xml 文件已生成，内容如下：")
    with open('feed.xml', 'r', encoding='utf-8') as f:
        print(f.read())

except Exception as e:
    print(f"出现错误: {e}")
