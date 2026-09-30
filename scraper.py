import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_amazon(self, asin):
        """Scrape Amazon product price"""
        url = f"https://www.amazon.com/dp/{asin}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract price using regex
            price_text = soup.find('span', {'class': re.compile(r'a-price-whole')})
            if price_text:
                price = re.findall(r'\d+\.\d+', price_text.text)
                return float(price[0]) if price else None
        except Exception as e:
            logger.error(f"Error scraping Amazon {asin}: {e}")
        return None
    
    def scrape_bestbuy(self, product_url):
        """Scrape Best Buy product price"""
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title and price
            title = soup.find('h1', {'class': 'heading-5'})
            price = soup.find('div', {'class': re.compile(r'priceView')})
            
            if price:
                price_match = re.search(r'\$(\d+\.\d+)', price.text)
                if price_match:
                    return float(price_match.group(1))
        except Exception as e:
            logger.error(f"Error scraping Best Buy: {e}")
        return None
    
    def parse_price(self, text):
        """Extract price from any text using regex"""
        match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        return float(match.group(1).replace(',', '')) if match else None
