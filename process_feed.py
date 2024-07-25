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

def extract_links_from_description(description):
    """ 从 description 中提取实际新闻链接 """
    links = []
    # 使用 BeautifulSoup 解析 description 中的 HTML
    soup = BeautifulSoup(description, 'lxml')
    for a_tag in soup.find_all('a', href=True):
        links.append(a_tag['href'])
    return links

def extract_actual_link_from_page(url):
    """ 从新闻页面中提取实际新闻链接 """
    html = fetch_html(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        
        # 尝试提取 og:url 元标签
        meta_tag = soup.find('meta', property='og:url')
        if meta_tag and meta_tag.get('content'):
            return meta_tag.get('content')
        
        # 尝试提取常见的新闻源链接
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'news' in href:  # 这里的条件可能需要根据实际情况调整
                return href
        
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
            
            # 从 description 中提取实际的新闻链接
            links = extract_links_from_description(description)
            actual_link = links[0] if links else link

            # 将描述中的第一个链接作为实际新闻链接
            description_cdata = escape_cdata(f"<![CDATA[{description}]]>")

            file.write(f"""
    <item>
      <title>{title}</title>
      <link>{actual_link}</link>
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
