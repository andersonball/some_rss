import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 获取实际新闻 URL
def fetch_real_news_url(google_news_url):
    try:
        response = requests.get(google_news_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根据网页结构提取实际的新闻 URL
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'example.com' in href:  # 使用实际新闻源域名替换
                return urljoin(google_news_url, href)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching real URL for {google_news_url}: {e}")
    
    # 如果未找到实际 URL，返回原 URL
    return google_news_url

# 从 RSS 中提取和转换链接
def fetch_and_convert_feed():
    RSS_URL = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
    try:
        response = requests.get(RSS_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing RSS XML: {e}")
        return []

    items = []
    url_map = {}  # 存储 google.com URL 与实际新闻地址的映射

    for item in root.findall('channel/item'):
        title = item.find('title').text if item.find('title') is not None else 'No Title'
        link = item.find('link').text if item.find('link') is not None else 'No Link'
        description = item.find('description').text if item.find('description') is not None else 'No Description'
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No PubDate'

        # 处理 link 和 description 中的 google.com 链接
        if 'news.google.com' in link:
            if link not in url_map:
                real_url = fetch_real_news_url(link)
                url_map[link] = real_url
            link = url_map[link]
        
        # 处理 description 中的所有链接
        soup = BeautifulSoup(description, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            url = a_tag['href']
            if 'news.google.com' in url:
                if url not in url_map:
                    real_url = fetch_real_news_url(url)
                    url_map[url] = real_url
                a_tag['href'] = url_map[url]

        description_modified = str(soup)

        # 处理 title 和 description，确保不含 google.com 和不提及名字
        title_modified = title.replace('google.com', '').strip()
        description_modified = description_modified.replace('google.com', '').strip()

        items.append({
            'title': title_modified,
            'link': link,
            'description': description_modified,
            'pubDate': pub_date
        })
    
    return items

# 创建新的 RSS feed 文件
def create_new_feed(items, filename='feed.xml'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Updated News Feed</title>
    <link>https://example.com/feed</link>
    <description>Updated news feed with real links</description>
""")
        for item in items:
            file.write(f"""
    <item>
      <title>{item['title']}</title>
      <link>{item['link']}</link>
      <description><![CDATA[{item['description']}]]></description>
      <pubDate>{item['pubDate']}</pubDate>
    </item>
""")
        file.write("""
  </channel>
</rss>""")
    print(f"New feed created and saved as {filename}")

def main():
    items = fetch_and_convert_feed()
    if items:
        create_new_feed(items)
    else:
        print("No items fetched or converted. Feed creation aborted.")

if __name__ == "__main__":
    main()
