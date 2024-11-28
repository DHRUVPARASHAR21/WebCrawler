# News Crawler

A Python-based news crawler that extracts stories matching specific keywords from online resources and posts them to Slack.

## Features
- Extracts news articles based on defined keywords.
- Automatically posts selected stories to a Slack channel.
- Tracks posted stories using SQLite to prevent duplicates.

## Prerequisites
- Python 3.x
- Libraries: `requests`, `BeautifulSoup`, `sqlite3`

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/username/news-crawler.git
   cd news-crawler
