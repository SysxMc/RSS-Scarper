import asyncio
import os
import random
import requests
from bs4 import BeautifulSoup
import logging
import subprocess
import json
from sub import * 
import xml.etree.ElementTree as ET



feed_filename = "./generated_pages/links.rss"




def create_rss_feed(items: list) -> str:
    # Create the root RSS element
    rss = ET.Element("rss", version="2.0")
    
    # Create the channel element
    channel = ET.SubElement(rss, "channel")
    
    # Add required channel elements
    ET.SubElement(channel, "title").text = "Sample RSS Feed"
    ET.SubElement(channel, "link").text = "https://example.com"
    ET.SubElement(channel, "description").text = "This is a sample RSS feed."
    
    # Create item elements from the list
    for item in items:
        title, link = item
        item_element = ET.SubElement(channel, "item")
        ET.SubElement(item_element, "title").text = title
        ET.SubElement(item_element, "link").text = link
    
    # Convert to a string
    return ET.tostring(rss, encoding="utf-8", method="xml").decode("utf-8")



async def fetch_all():
    existing_links = set()
    if os.path.exists(feed_filename):
        with open(feed_filename, 'r') as feed:
            existing_links = set(line.strip().split('|-|')[-1] for line in feed)  
    new_links = []
    mislinks = await extract_missav("https://missav.ws/dm561/en/uncensored-leak", end_page=2)
    for link in mislinks:
        if link[-1] not in existing_links:  # Check if link is new
            src_result = await crawl_missav(link[-1])  # Await the coroutine
            src = src_result[-1]  # Access the last element of the returned result
            link.append(src)
            new_links.append([link[0],link[-1]])
    vids = extract_hanime()
    for vid in vids:
        if vid[-1] not in existing_links:
            new_links.append(vid)
    vids = extract_htv()
    for vid in vids:
        if vid[-1] not in existing_links:
            new_links.append(vid)
    return new_links

async def main():
    new_links = await fetch_all()
    rss_feed = create_rss_feed(new_links)
    os.makedirs("./generated_pages", exist_ok=True)
    with open(feed_filename, "w", encoding="utf-8") as f:
        f.write(rss_feed)

if __name__ == "__main__":
    asyncio.run(main())
