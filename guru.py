import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
import uvicorn
import asyncio
from crawl4ai import AsyncWebCrawler

app = FastAPI()

crawler = AsyncWebCrawler()
   
all_data = []


@app.get("/")
def read_root():
    return {"message": "Welcome to the JAV Torrents RSS Feed!"}


@app.get("/rss")
def serve_rss():
    file_path = "torrents.rss"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/rss+xml")
    return {"error": "RSS feed not found"}


def torrents_to_rss(torrents):
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "JAV Torrents"
    unique_torrents = {t["title"]: t for t in torrents}.values()
    for torrent in unique_torrents:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = torrent["title"]
        ET.SubElement(item, "link").text = torrent["download_link"]
        ET.SubElement(item, "description").text = f"{torrent['size']} - {torrent['seeders']} seeders"
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    return ET.tostring(rss, encoding="unicode")



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
                "Code":jav_data["Code"],
                "Poster":jav_data["Poster"],
                "Code":jav_data["Code"],
                "Release Date":jav_data["Release Date"],
                "Views":jav_data["Views"],
                "Screenshots":jav_data["Screenshots"],
                "title": cols[1].get_text(strip=True),
                "download_link": "https://sukebei.nyaa.si" + cols[2].find("a")["href"]
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


def fetch_torrent(url):
    try:
        jav_data = fetch_data(url)
        if not jav_data:
            return
        results = search_sukebei(jav_data)
        for torrent in results:
            data.append(torrent)
    except Exception as e:
        print(f"Fetch Torrent Error: {e}")




async def fetch_data(url):
    async with crawler:
        result = await crawler.arun(url)
        images = [ img["src"] for img in result.media["images"] if img["src"] and img["src"].endswith(".jpg") and img["src"].split("/")[-1] != "customfield1005.jpg" ]
        response = result.html
        soup = BeautifulSoup(response, "html.parser")
        match = [ re.search(pattern, soup.get_text()).group(1) for pattern in [r"Code:\s*(\S+)",r"Release Date:\s*(\S+)", r"\s*(\S+) views",r"\b([A-Z]+-\d+)\b"]][:3]
        if match:
             return {"Poster":images[0],"Code":match[0],"Release Date":match[1],"Views":match[2],"Screenshots":images[1:]}


async def get_links(link):
     async with crawler:
        result = await crawler.arun(url=link)
        links = result.links["internal"]
        valid_links = [ link for link in links if len(link["href"].split("/")) > 4 and link["href"].split("/")[3].isdigit() ]
        return valid_links


def main():
    for i in range(1, 31):
        try:
            links = get_links(f"https://jav.guru/page/{i}/")
            for link in links:
                fetch_torrent(link)
        except Exception as e:
            print(f"Main Process Error on page {i}: {e}")

    try:
        rss_feed = torrents_to_rss(data)
        with open("torrents.rss", "w", encoding="utf-8") as f:
            f.write(rss_feed)
    except Exception as e:
        print(f"RSS Generation Error: {e}")


if __name__ == "__main__":
    await main()
    uvicorn.run(app, host="0.0.0.0", port=80)
