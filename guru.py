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

app = FastAPI()

data = []


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


def extract_jav_code(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for pattern in [r"Code:\s*(\S+)", r"\b([A-Z]+-\d+)\b"]:
            match = re.search(pattern, soup.get_text())
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Code Extraction Error: {e}")
    return None


def parse_size(size_str):
    try:
        size_num = float(size_str.split()[0])
        unit = size_str.split()[1].lower()

        if unit == "gb":
            return size_num
        elif unit == "mb":
            return size_num / 1024
        return size_num
    except (ValueError, IndexError):
        return float("inf")


def search_sukebei(code):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(
            f"https://sukebei.nyaa.si/?q={code}&s=downloads&o=desc", headers=headers, timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")

        results = [
            {
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
        jav_code = extract_jav_code(url)
        if not jav_code:
            return

        results = search_sukebei(jav_code)
        for torrent in results:
            data.append(torrent)
    except Exception as e:
        print(f"Fetch Torrent Error: {e}")


def get_links(url):
    try:
        response = requests.get(url, timeout=10)
        return list(
            {
                urljoin(url, a["href"])
                for a in BeautifulSoup(response.text, "html.parser").find_all(
                    "a", href=True
                )
            }
        )
    except Exception as e:
        print(f"Link Extraction Error: {e}")
        return []


def main():
    for i in range(1, 31):
        try:
            links = get_links(f"https://jav.guru/page/{i}/")
            valid_links = [
                link
                for link in links
                if len(link.split("/")) > 4 and link.split("/")[3].isdigit()
            ]
            for link in valid_links:
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
    main()
    # Running on port 80 may require root permissions. Change to port 8000 if needed.
    uvicorn.run(app, host="0.0.0.0", port=80)
