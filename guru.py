import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime
import asyncio
from crawl4ai import AsyncWebCrawler
import os

crawler = AsyncWebCrawler()
all_data = []


def torrents_to_rss(torrents):
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "JAV Torrents"
    
    unique_torrents = {f"{t['title']}-{t['download_link']}": t for t in torrents}.values()
    
    for torrent in unique_torrents:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = torrent["title"]
        ET.SubElement(item, "link").text = torrent["download_link"]
        description = (
            f"Size: {torrent['size']} - {torrent['seeders']} seeders<br>"
            f"Code: {torrent.get('Code', 'N/A')}<br>"
            f"Release Date: {torrent.get('Release Date', 'N/A')}<br>"
            f"Views: {torrent.get('Views', 'N/A')}<br>"
            f"<img src='{torrent.get('Poster', '')}' alt='Poster'><br>"
        )
        for screenshot in torrent.get("Screenshots", []):
            description += f"<img src='{screenshot}' alt='Screenshot'><br>"
        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    return ET.tostring(rss, encoding="unicode")


def parse_size(size_str):
    try:
        size, unit = re.match(r"([\d.]+)\s*(\w+)", size_str).groups()
        size = float(size)
        if unit.lower().startswith("g"):
            return size
        elif unit.lower().startswith("m"):
            return size / 1024
    except Exception:
        return float("inf")


def search_sukebei(jav_data):
    try:
        jav_code = jav_data["Code"]
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(
            f"https://sukebei.nyaa.si/?q={jav_code}&s=downloads&o=desc", headers=headers, timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = [
            {
                "Poster": jav_data["Poster"],
                "Code": jav_data["Code"],
                "Release Date": jav_data["Release Date"],
                "Views": jav_data["Views"],
                "Screenshots": jav_data["Screenshots"],
                "title": cols[1].get_text(strip=True),
                "download_link": urljoin("https://sukebei.nyaa.si", cols[2].find("a")["href"])
                if cols[2].find("a")
                else None,
                "size": cols[3].get_text(strip=True),
                "seeders": cols[5].get_text(strip=True) if len(cols) > 5 else "N/A",
            }
            for row in soup.select("table.table tbody tr")
            if (cols := row.find_all("td")) and len(cols) >= 4
        ]

        return [
            r
            for r in results
            if "720" in r["title"].lower() and parse_size(r["size"]) <= 1.9
        ][:1]
    except Exception as e:
        print(f"Sukebei Search Error: {e}")
        return []


async def fetch_data(url):
    try:
        async with crawler:
            result = await crawler.arun(url)
            images = [
                img["src"]
                for img in result.media["images"]
                if img["src"] and img["src"].endswith(".jpg") and img["src"].split("/")[-1] != "customfield1005.jpg"
            ]
            soup = BeautifulSoup(result.html, "html.parser")
            patterns = [r"Code:\s*(\S+)", r"Release Date:\s*(\S+)", r"\s*(\S+) views"]
            matches = [re.search(pattern, soup.get_text()) for pattern in patterns]
            extracted = [m.group(1) for m in matches if m]
            if len(extracted) == 3:
                return {
                    "Poster": images[0] if images else None,
                    "Code": extracted[0],
                    "Release Date": extracted[1],
                    "Views": extracted[2],
                    "Screenshots": images[1:],
                }
    except Exception as e:
        print(f"Fetch Data Error: {e}")


async def get_links(link):
    try:
        async with crawler:
            result = await crawler.arun(url=link)
            links = result.links["internal"]
            return [
                l["href"]
                for l in links
                if len(l["href"].split("/")) > 4 and l["href"].split("/")[3].isdigit()
            ]
    except Exception as e:
        print(f"Get Links Error: {e}")
        return []


async def main():
    try:
        for i in range(1,5):
            try:
                links = await get_links(f"https://jav.guru/page/{i}/")
                for link in links:
                    jav_data = await fetch_data(link)
                    print(jav_data)
                    if jav_data:
                        torrents = search_sukebei(jav_data)
                        print(torrents)
                        all_data.extend(torrents)
            except Exception as e:
                print(f"Main Process Error on page {i}: {e}")

        rss_feed = torrents_to_rss(all_data)
        os.makedirs("./generated_pages", exist_ok=True)
        with open("./generated_pages/torrents.rss", "w", encoding="utf-8") as f:
            f.write(rss_feed)
    except Exception as e:
        print(f"RSS Generation Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
