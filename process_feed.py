import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape

def fetch_html(url):
    """ 获取网页内容 """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

def extract_actual_link_from_page(url):
    """ 从新闻页面中提取实际新闻链接 """
    html = fetch_html(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        meta_tag = soup.find('meta', property='og:url')
        if meta_tag:
            return meta_tag.get('content')
    return url

def escape_cdata(data):
    """ 处理可能的 CDATA 区域中的特殊字符 """
    return data.replace(']]>', ']]]]><![CDATA[>')

def escape_xml_chars(data):
    """ 转义 XML 中的特殊字符 """
    return escape(data)

def create_final_feed(items, filename='new-feed.xml'):
    feed_url = 'https://andersonball.github.io/some_rss/new-feed.xml'
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

            actual_link = extract_actual_link_from_page(link)
            if actual_link:
                link = actual_link

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
    tree = ET.parse('feed.xml')
    root = tree.getroot()
    items = root.find('channel').findall('item')
    create_final_feed(items)
    print("new-feed.xml 文件已生成，内容如下：")
    with open('new-feed.xml', 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == "__main__":
    main()
