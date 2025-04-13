import requests
from bs4 import BeautifulSoup
import time
import random

def get_user_agent():
    """Return a random user agent string to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    ]
    return random.choice(user_agents)

def create_headers():
    """Create request headers with a random user agent."""
    return {
        'User-Agent': get_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

def fetch_webpage(url):
    """Fetch a webpage and return the response object."""
    try:
        headers = create_headers()
        response = requests.get(url, headers=headers, timeout=10)
        
        # Add a small delay to be respectful to the server
        time.sleep(random.uniform(1, 3))
        
        if response.status_code == 200:
            print(f"Successfully fetched: {url}")
            return response
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html_content):
    """Parse HTML content using BeautifulSoup."""
    return BeautifulSoup(html_content, 'html.parser')

def extract_video_links(soup, base_url=None):
    """Extract video links from parsed HTML."""
    links = soup.find_all('a')
    video_links = []
    
    for link in links:
        href = link.get('href')
        if href and "/video/" in href:
            # Handle relative URLs if a base_url is provided
            if base_url and href.startswith('/'):
                href = base_url.rstrip('/') + href
            video_links.append(href)
    
    return video_links

def extract_video_sources(soup, base_url=None, video_id=None):
    """Extract video sources from <video> tags in HTML."""
    if video_id:
        video_tags = soup.find_all('video', id=video_id)
    else:
        video_tags = soup.find_all('video')
    
    video_sources = []
    
    for video in video_tags:
        video_id = video.get('id', '')
        sources = video.find_all('source')
        
        for source in sources:
            src = source.get('src', '')
            title = source.get('title', '')
            type_attr = source.get('type', '')
            
            if base_url and src and src.startswith('/'):
                src = base_url.rstrip('/') + src
                
            if src:
                video_sources.append({
                    'video_id': video_id,
                    'src': src,
                    'title': title,
                    'type': type_attr
                })
    
    return video_sources

def get_thisplayer_video(soup, base_url=None):
    """Specifically extract video sources with ID 'thisPlayer'."""
    return extract_video_sources(soup, base_url, video_id="thisPlayer")

def save_video_sources_to_file(video_sources, filename="video_sources.txt"):
    """Save extracted video sources to a text file."""
    with open(filename, 'w+') as f:
        for source in video_sources:
            f.write(f"{source['src']}\n")
    print(f"Saved {len(video_sources)} video sources to {filename}")

def main(url):
    """Main function to scrape index and process video links."""
    # Fetch the index page
    response = fetch_webpage(url)
    if not response:
        return
    
    if "Sorry" in response.text:
        print("Reached the End.!,Exciting Now!!!!")
        exit()
    # Extract base URL (this is used to handle relative links)
    base_url = '/'.join(url.split('/')[:3])
    
    # Parse the index page HTML
    soup = parse_html(response.content)
    
    # Extract video links from index page
    video_links = extract_video_links(soup, base_url)
    print(f"Found {len(video_links)} video links on the index page.")
    
    # Process each video link
    all_video_sources = []
    for video_url in video_links:
        print(f"Processing video: {video_url}")
        video_response = fetch_webpage(video_url)
        
        if not video_response:
            continue
        
        # Parse the individual video page HTML
        video_soup = parse_html(video_response.content)
        
        # Extract video sources (e.g., from <video> tags)
        video_sources = get_thisplayer_video(video_soup, base_url)
        print(video_sources[0]["src"])
        all_video_sources.extend(video_sources)
    
    # Save the extracted video sources to a file
    save_video_sources_to_file(all_video_sources, "./generated_pages/draft_videos.txt")

if __name__ == "__main__":
    # Start scraping from the index page
    page = 1
    while True:
         target_url = f'https://draftsex.porn/page{page}.html'  # Change this to the index URL
         main(target_url)
         page+=1
              
