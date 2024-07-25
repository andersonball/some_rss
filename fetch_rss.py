import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

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
    for item in root.findall('channel/item'):
        title = item.find('title').text if item.find('title') is not None else 'No Title'
        link = item.find('link').text if item.find('link') is not None else 'No Link'
        description = item.find('description').text if item.find('description') is not None else 'No Description'
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No PubDate'

        # 修改 description 中的链接
        soup = BeautifulSoup(description, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if 'news.google.com' in url:
                real_url = convert_to_real_url(url)
                link['href'] = real_url
        
        # 确保 <link> 字段中的链接也被替换
        if 'news.google.com' in link:
            link = convert_to_real_url(link)

        description_modified = str(soup)
        items.append({
            'title': title,
            'link': link,
            'description': description_modified,
            'pubDate': pub_date
        })
    
    return items

def convert_to_real_url(url):
    # 示例替换逻辑，你需要提供实际的转换逻辑
    return url.replace('news.google.com', 'real-news-source.com')  # 示例替换逻辑

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
