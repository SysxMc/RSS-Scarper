import asyncio
import os
import random
import requests
from bs4 import BeautifulSoup
import logging
import subprocess
import json
from sub import * 

feed_filename = "links.txt"

async def fetch_all():
    existing_links = set()
    if os.path.exists(feed_filename):
        with open(feed_filename, 'r') as feed:
            existing_links = set(line.strip().split('|-|')[-1] for line in feed)  
    new_links = []
    mislinks = await extract_missav("https://missav.com/dm561/en/uncensored-leak", end_page=2)
    for link in mislinks:
        if link[-1] not in existing_links:  # Check if link is new
            src_result = await crawl_missav(link[-1])  # Await the coroutine
            src = src_result[-1]  # Access the last element of the returned result
            link.append(src)
            new_links.append(link)
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
    all_links = set()
    if os.path.exists(feed_filename):
        with open(feed_filename, 'r') as feed:
            all_links = set(feed.read().splitlines())
    for link in new_links:
        all_links.add("|-|".join(link))
    with open(feed_filename, 'w+') as feed:
        for link in all_links:
            feed.write(link + "\n")
    #print(new_links)

if __name__ == "__main__":
    asyncio.run(main())
