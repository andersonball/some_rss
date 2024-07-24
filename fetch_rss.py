import requests
import feedparser
import os

# 你的 RSS 源 URL
rss_url = "https://news.google.com/rss"

# 如果需要 token，设置请求头部
headers = {
    'Authorization': 'Bearer ' + os.getenv('ACCESS_TOKEN')  # 从环境变量中读取 token
}

# 发送请求并获取响应
response = requests.get(rss_url, headers=headers)

if response.status_code == 200:
    feed = feedparser.parse(response.content)
else:
    print(f"Failed to fetch RSS feed: {response.status_code}")
    exit(1)

# 创建或更新 feed.xml 文件
with open("feed.xml", "w", encoding="utf-8") as file:
    file.write(f"<?xml version='1.0' encoding='UTF-8'?>\n")
    file.write(f"<rss version='2.0'>\n")
    file.write(f"  <channel>\n")
    file.write(f"    <title>{feed.feed.title}</title>\n")
    file.write(f"    <link>{feed.feed.link}</link>\n")
    file.write(f"    <description>{feed.feed.description}</description>\n")

    for entry in feed.entries:
        title = entry.title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        description = entry.description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        file.write(f"    <item>\n")
        file.write(f"      <title>{title}</title>\n")
        file.write(f"      <link>{entry.link}</link>\n")
        file.write(f"      <description>{description}</description>\n")
        file.write(f"      <pubDate>{entry.published}</pubDate>\n")
        file.write(f"    </item>\n")

    file.write(f"  </channel>\n")
    file.write(f"</rss>\n")

