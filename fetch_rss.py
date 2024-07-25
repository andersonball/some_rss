import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from aiohttp import ClientSession

# 中文 RSS 源地址
RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'

async def fetch(session, url):
    """ 异步获取网页内容 """
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # 确保请求成功
            return await response.text()
    except Exception as e:
        print(f"请求链接失败: {e}")
        return None

async def get_redirected_url(session, url):
    """ 从 Google News 链接中获取实际的新闻源链接 """
    html = await fetch(session, url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        link_tag = soup.find('meta', property='og:url')
        if link_tag:
            return link_tag.get('content')
    return url

async def extract_actual_link(session, description):
    """ 从 description 中提取 Google News 链接并转换为实际的新闻源链接 """
    soup = BeautifulSoup(description, 'lxml')
    links = soup.find_all('a')
    tasks = []
    for link in links:
        href = link.get('href')
        if href and href.startswith('https://news.google.com/rss/articles/'):
            tasks.append(get_redirected_url(session, href))
    results = await asyncio.gather(*tasks)
    for result in results:
        if result:
            return result
    return ''

async def process_items(items):
    """ 处理 RSS 项目并生成新的 RSS 文件 """
    async with ClientSession() as session:
        tasks = []
        for item in items:
            title = item.find('title').text or ''
            link = item.find('link').text or ''
            description = item.find('description').text or ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '无日期'

            # 尝试从 description 中提取实际新闻链接
            actual_link = await extract_actual_link(session, description)
            if actual_link:
                link = actual_link  # 替换为实际的新闻链接

            # 处理描述中的特殊字符（可能包含 HTML 标记）
            description = escape_xml_chars(description)

            # 保存每个 item 的结果
            tasks.append({
                'title': title,
                'link': link,
                'description': description,
                'pubDate': pub_date,
            })

        # 创建 feed.xml 文件
        create_feed(tasks)

def escape_xml_chars(data):
    """ 转义 XML 中的特殊字符 """
    return data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

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
            # 写入每个 item
            file.write(f"""
    <item>
      <title>{item['title']}</title>
      <link>{item['link']}</link>
      <description>{item['description']}</description>
      <pubDate>{item['pubDate']}</pubDate>
    </item>
""")
        
        # 结束 XML 文件
        file.write("""
  </channel>
</rss>""")

async def main():
    """ 主函数 """
    try:
        # 请求 RSS 源
        async with aiohttp.ClientSession() as session:
            rss_response = await fetch(session, RSS_URL)
            if rss_response:
                # 解析 RSS XML
                root = ET.fromstring(rss_response)
                # 获取 RSS 频道中的项
                items = root.find('channel').findall('item')
                await process_items(items)
                print("feed.xml 文件已生成，内容如下：")
                with open('feed.xml', 'r', encoding='utf-8') as f:
                    print(f.read())
    except Exception as e:
        print(f"出现错误: {e}")

# 运行主函数
asyncio.run(main())
