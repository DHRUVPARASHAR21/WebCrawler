import requests
from bs4 import BeautifulSoup
import random
import json
import sqlite3
import re
from urllib.parse import urljoin

class NewsCrawler:
    def __init__(self, keywords, resources, slack_webhook):
        self.keywords = keywords
        self.resources = resources
        self.slack_webhook = slack_webhook
        self.db_path = 'posted_stories.db'
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database to track posted stories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                url TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _is_story_posted(self, url):
        """Check if story has been previously posted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stories WHERE url = ?', (url,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def _save_posted_story(self, url, title, summary):
        """Save posted story to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO stories (url, title, summary) VALUES (?, ?, ?)', 
                       (url, title, summary))
        conn.commit()
        conn.close()

    def _extract_story(self, url):
        """Generic story extraction method"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Different extraction strategies based on site
            title = self._extract_title(soup, url)
            summary = self._extract_summary(soup, url)

            return title, summary
        except Exception as e:
            print(f"Error extracting from {url}: {e}")
            return None, None

    def _extract_title(self, soup, url):
        """Extract title with fallback methods"""
        title_selectors = [
            'h1', '.entry-title', 'article h1', 'title', 
            '.article-title', '#main-title'
        ]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and len(title_elem.get_text(strip=True)) > 5:
                return title_elem.get_text(strip=True)
        return f"Story from {url}"

    def _extract_summary(self, soup, url):
        """Extract summary with multiple strategies"""
        summary_selectors = [
            '.entry-content p', 'article p', '.article-body p', 
            '.content p', '#main-content p'
        ]
        for selector in summary_selectors:
            paragraphs = soup.select(selector)
            for p in paragraphs:
                text = p.get_text(strip=True)
                if 20 < len(text) < 300:
                    return text
        return "No summary available"

    def _keyword_match(self, text):
        """Check if text matches any keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)

    def find_matching_story(self):
        """Find a story matching keywords that hasn't been posted"""
        random.shuffle(self.resources)
        for resource in self.resources:
            try:
                response = requests.get(resource, timeout=10, 
                    headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract links from various possible sources
                links = soup.find_all('a', href=True)
                random.shuffle(links)

                for link in links:
                    full_url = urljoin(resource, link['href'])
                    
                    # Skip if story already posted or looks like an invalid link
                    if (self._is_story_posted(full_url) or 
                        any(x in full_url.lower() for x in 
                            ['#', 'javascript:', 'mailto:', '.pdf', '.jpg', '.png'])):
                        continue

                    link_text = link.get_text(strip=True)
                    if not self._keyword_match(link_text):
                        continue

                    title, summary = self._extract_story(full_url)
                    
                    if title and summary and self._keyword_match(title + " " + summary):
                        return title, summary, full_url

            except Exception as e:
                print(f"Error processing {resource}: {e}")
        
        return None, None, None

    def post_to_slack(self, title, summary, url):
        """Post story to Slack"""
        payload = {
            "text": f"*{title}*\n\n{summary}\n\nRead more: {url}"
        }
        try:
            response = requests.post(self.slack_webhook, json=payload)
            if response.status_code == 200:
                self._save_posted_story(url, title, summary)
                return True
        except Exception as e:
            print(f"Slack posting error: {e}")
        return False

def main():
    keywords = [
      
    ]
    
    resources = [
         
        
    ]

    slack_webhook = ('Enter Link')

    crawler = NewsCrawler(keywords, resources, slack_webhook)
    
    title, summary, url = crawler.find_matching_story()
    
    if title and summary and url:
        crawler.post_to_slack(title, summary, url)
        print(f"Posted: {title}")
    else:
        print("No matching stories found.")

if __name__ == "__main__":
    main()