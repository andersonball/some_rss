import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def fetch_feed(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def extract_google_news_links(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    
    google_news_links = set()
    for item in root.findall('.//item'):
        link_elem = item.find('link')
        if link_elem is not None:
            url = link_elem.text
            if 'news.google.com' in url:
                google_news_links.add(url)
    return google_news_links

def fetch_real_news_url(google_news_url):
    # 发起请求
    response = requests.get(google_news_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 示例: 假设真实新闻源地址在 <a> 标签中，通常新闻页面会有这样的链接
    # 这个具体的解析逻辑需要根据实际网页结构调整
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and 'example.com' in href:
            return urljoin(google_news_url, href)
    
    # 如果未找到真实 URL，返回原 URL
    return google_news_url

def replace_links_in_feed(xml_content, url_map):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    for item in root.findall('.//item'):
        link_elem = item.find('link')
        if link_elem is not None:
            old_url = link_elem.text
            new_url = url_map.get(old_url, old_url)
            link_elem.text = new_url

    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

def save_feed(xml_content, output_file):
    with open(output_file, 'wb') as f:
        f.write(xml_content)

def main(feed_url, output_file):
    # 获取原始 feed.xml 内容
    xml_content = fetch_feed(feed_url)
    
    # 提取谷歌新闻链接
    google_news_links = extract_google_news_links(xml_content)
    
    # 构建 URL 映射表
    url_map = {}
    for url in google_news_links:
        real_url = fetch_real_news_url(url)
        url_map[url] = real_url
    
    # 替换链接
    updated_xml_content = replace_links_in_feed(xml_content, url_map)
    
    # 保存新的 feed.xml
    save_feed(updated_xml_content, output_file)
    print(f"Updated feed saved as {output_file}")

# 使用示例
feed_url = 'https://example.com/feed.xml'  # 输入你实际的 feed.xml URL
output_file = 'new-feed.xml'
main(feed_url, output_file)
