# RSS Aggregator and Telegram Uploader Bot  

This repository contains a Python-based tool that combines multiple RSS feeds and web-scraped links into a single RSS feed. The tool can also download the content and upload it to Telegram as an archive.  

## Features  
- **RSS Feed Aggregation:** Merge multiple RSS feeds into one unified feed.  
- **Web Scraping:** Extract direct download links from specified websites.  
- **Content Downloading:** Automatically download content from aggregated feeds or scraped links.  
- **Telegram Integration:** Upload downloaded content to a Telegram channel or group as an archive.  

## Requirements  
- Python 3.8+  
- Required Libraries:  
  ```bash  
  pip install -r requirements.txt

Installation

1. Clone this repository:

git clone https://github.com/yourusername/rss-aggregator-telegram.git  
cd rss-aggregator-telegram


2. Install dependencies:

pip install -r requirements.txt


3. Set up a Telegram Bot using BotFather and get the bot token.


4. Create a .env file to store your configuration:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token  
TELEGRAM_CHAT_ID=your_target_chat_id



Usage

1. Configure Feeds and Websites:

Add your RSS feed URLs and website URLs to the config.yaml file. Example:

rss_feeds:  
  - https://example.com/feed  
  - https://another-site.com/rss  

websites:  
  - https://example.com/downloads



2. Run the Script:

python main.py


3. The script will:

Aggregate RSS feeds into a single feed.

Scrape download links from specified websites.

Download content and upload it to your Telegram channel or group.




Configuration

RSS Feed Parsing: Uses feedparser for handling RSS feeds.

Web Scraping: Uses BeautifulSoup for scraping direct links from websites.

Telegram Bot: Uses pyrogram for Telegram API integration.


Example Output

Aggregated RSS feed format:

<rss version="2.0">  
  <channel>  
    <title>Aggregated Feed</title>  
    <link>https://youraggregator.com/feed</link>  
    <description>Combined RSS Feed from multiple sources</description>  
    <item>  
      <title>Item Title</title>  
      <link>https://example.com/item1</link>  
      <description>Item description</description>  
    </item>  
  </channel>  
</rss>

Contribution

Contributions are welcome! Please open an issue or create a pull request for improvements.

License

This project is licensed under the MIT License. See the LICENSE file

