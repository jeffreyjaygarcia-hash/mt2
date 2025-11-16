import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
from database import MemorabiliaDatabase

class MemorabilliaScraper:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.db = MemorabiliaDatabase()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_all(self):
        """Main scraping function - runs all enabled platforms"""
        print(f"Starting scrape at {datetime.now()}")
        
        # Scrape for Tier 1 players
        for player in self.config['tier1_players']['players']:
            self.scrape_player(player, 'tier1', price_max=None)
        
        # Scrape for Tier 2 players
        for player in self.config['tier2_players']['players']:
            self.scrape_player(
                player, 'tier2',
                price_min=self.config['tier2_players']['price_min'],
                price_max=self.config['tier2_players']['price_max']
            )
        
        # Scrape for golf players
        for player in self.config['golf_players']['players']:
            self.scrape_player(
                player, 'golf',
                price_min=self.config['golf_players']['price_min'],
                price_max=self.config['golf_players']['price_max']
            )
        
        print(f"Scrape completed at {datetime.now()}")
    
    def scrape_player(self, player: str, tier: str, 
                     price_min: Optional[float] = None,
                     price_max: Optional[float] = None):
        """Scrape all platforms for a specific player"""
        print(f"Scraping {player} ({tier})...")
        
        if self.config['platforms']['ebay']['enabled']:
            self.scrape_ebay(player, tier, price_min, price_max)
        
        # Other platforms would be added here
        # self.scrape_pwcc(player, tier, price_min, price_max)
        # self.scrape_goldin(player, tier, price_min, price_max)
        
        time.sleep(2)  # Rate limiting
    
    def scrape_ebay(self, player: str, tier: str,
                   price_min: Optional[float] = None,
                   price_max: Optional[float] = None):
        """Scrape eBay for player memorabilia"""
        
        # Build search query
        search_terms = [
            f"{player} autographed",
            f"{player} signed",
            f"{player} game used"
        ]
        
        for search_term in search_terms:
            # Scrape current listings
            self._scrape_ebay_listings(search_term, player, tier, price_min, price_max, completed=False)
            
            # Scrape sold listings for price history
            if self.config['platforms']['ebay']['search_completed']:
                self._scrape_ebay_listings(search_term, player, tier, price_min, price_max, completed=True)
            
            time.sleep(1)
    
    def _scrape_ebay_listings(self, search_term: str, player: str, tier: str,
                             price_min: Optional[float], price_max: Optional[float],
                             completed: bool = False):
        """Internal method to scrape eBay listings or sold items"""
        
        # Build eBay search URL
        base_url = "https://www.ebay.com/sch/i.html"
        params = {
            '_nkw': search_term,
            '_sop': 12,  # Sort by ending soonest
            'LH_ItemCondition': 3000,  # Used
            'rt': 'nc'
        }
        
        if completed:
            params['LH_Complete'] = 1
            params['LH_Sold'] = 1
        
        if price_min:
            params['_udlo'] = price_min
        if price_max:
            params['_udhi'] = price_max
        
        try:
            response = requests.get(base_url, params=params, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse listings
            listings = soup.find_all('div', {'class': 's-item__wrapper'})
            
            for listing in listings[:20]:  # Process first 20 results
                try:
                    listing_data = self._parse_ebay_listing(listing, player, tier, completed)
                    if listing_data:
                        if completed:
                            # Add to price history
                            self.db.add_price_history(listing_data)
                        else:
                            # Add to active listings
                            self.db.add_listing(listing_data)
                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping eBay for {search_term}: {e}")
    
    def _parse_ebay_listing(self, listing_html, player: str, tier: str, completed: bool) -> Optional[Dict]:
        """Parse individual eBay listing HTML"""
        try:
            # Extract title
            title_elem = listing_html.find('div', {'class': 's-item__title'})
            title = title_elem.text.strip() if title_elem else None
            
            if not title or title == "Shop on eBay":
                return None
            
            # Extract price
            price_elem = listing_html.find('span', {'class': 's-item__price'})
            price_text = price_elem.text.strip() if price_elem else None
            
            if not price_text:
                return None
            
            # Clean price
            price = float(re.sub(r'[^\d.]', '', price_text.split('to')[0]))
            
            # Extract URL
            url_elem = listing_html.find('a', {'class': 's-item__link'})
            url = url_elem['href'] if url_elem else None
            
            # Extract image
            img_elem = listing_html.find('img')
            image_url = img_elem['src'] if img_elem else None
            
            # Extract listing ID from URL
            listing_id = None
            if url:
                match = re.search(r'/(\d+)\?', url)
                listing_id = match.group(1) if match else None
            
            # Detect authentication
            authentication = self._detect_authentication(title)
            
            # Detect inscriptions
            inscription = self._detect_inscription(title)
            
            # Detect item type
            item_type = self._detect_item_type(title)
            
            # Detect game used
            game_used = any(term in title.lower() for term in ['game used', 'game worn', 'game issued'])
            
            # Extract end date (if available)
            end_date = None
            if not completed:
                time_elem = listing_html.find('span', {'class': 's-item__time-left'})
                if time_elem:
                    end_date = self._parse_end_date(time_elem.text.strip())
            
            listing_data = {
                'listing_id': listing_id or f"ebay_{hash(url)}",
                'platform': 'ebay',
                'player_name': player,
                'tier': tier,
                'title': title,
                'price': price,
                'url': url,
                'image_url': image_url,
                'authentication': authentication,
                'cert_number': None,  # Would need to scrape listing page
                'item_type': item_type,
                'inscription': inscription,
                'condition': None,  # Would need to scrape listing page
                'seller': None,  # Would need to scrape listing page
                'seller_rating': None,
                'end_date': end_date,
                'game_used': game_used,
                'status': 'sold' if completed else 'active',
                'raw_data': {}
            }
            
            # For completed listings, use different field names
            if completed:
                listing_data['sale_price'] = price
                listing_data['sale_date'] = datetime.now().isoformat()
            
            return listing_data
            
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None
    
    def _detect_authentication(self, title: str) -> Optional[str]:
        """Detect authentication service from title"""
        title_lower = title.lower()
        for auth in self.config['authentication_services']:
            if auth.lower() in title_lower:
                return auth
        return None
    
    def _detect_inscription(self, title: str) -> Optional[str]:
        """Detect and extract inscription from title"""
        title_lower = title.lower()
        
        # Check all inscription patterns
        for category, patterns in self.config['inscription_patterns'].items():
            for pattern in patterns:
                if pattern.lower() in title_lower:
                    # Try to extract the actual inscription
                    # Look for text in quotes
                    quote_match = re.search(r'"([^"]+)"', title)
                    if quote_match:
                        return quote_match.group(1)
                    # Look for "insc:" or "inscribed:"
                    insc_match = re.search(r'insc(?:ribed)?:?\s*([^,\-]+)', title_lower)
                    if insc_match:
                        return insc_match.group(1).strip()
                    # Return the pattern we found
                    return pattern
        return None
    
    def _detect_item_type(self, title: str) -> Optional[str]:
        """Detect item type from title"""
        title_lower = title.lower()
        
        type_keywords = {
            'jersey': ['jersey', 'authentic', 'swingman'],
            'ball': ['baseball', 'football', 'basketball'],
            'photo': ['photo', '8x10', '16x20', 'photograph'],
            'bat': ['bat'],
            'helmet': ['helmet'],
            'glove': ['glove'],
            'cleats': ['cleats', 'shoes'],
            'flag': ['flag', 'flagstick']
        }
        
        for item_type, keywords in type_keywords.items():
            if any(kw in title_lower for kw in keywords):
                return item_type
        
        return 'other'
    
    def _parse_end_date(self, time_text: str) -> Optional[str]:
        """Parse eBay time remaining text to end date"""
        try:
            # Parse patterns like "2d 3h" or "5h 20m"
            days = hours = minutes = 0
            
            day_match = re.search(r'(\d+)d', time_text)
            if day_match:
                days = int(day_match.group(1))
            
            hour_match = re.search(r'(\d+)h', time_text)
            if hour_match:
                hours = int(hour_match.group(1))
            
            min_match = re.search(r'(\d+)m', time_text)
            if min_match:
                minutes = int(min_match.group(1))
            
            end_date = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
            return end_date.isoformat()
            
        except Exception:
            return None

if __name__ == "__main__":
    scraper = MemorabilliaScraper()
    scraper.scrape_all()
