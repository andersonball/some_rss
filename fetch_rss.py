import feedparser
import requests

# 定义要抓取的 RSS 源
RSS_URL = "https://news.google.com/rss"

# 抓取 RSS 数据
response = requests.get(RSS_URL)
rss_data = response.text

# 解析 RSS 数据
feed = feedparser.parse(rss_data)

# 创建/更新 feed.xml 文件
with open("feed.xml", "w", encoding="utf-8") as file:
    file.write("<rss version='2.0'>\n")
    file.write("<channel>\n")
    file.write(f"<title>{feed.feed.title}</title>\n")
    file.write(f"<link>{feed.feed.link}</link>\n")
    file.write(f"<description>{feed.feed.description}</description>\n")

    for entry in feed.entries:
        file.write("<item>\n")
        file.write(f"<title>{entry.title}</title>\n")
        file.write(f"<link>{entry.link}</link>\n")
        file.write(f"<description>{entry.description}</description>\n")
        file.write("</item>\n")

    file.write("</channel>\n")
    file.write("</rss>\n")
