import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class MemorabiliaDatabase:
    def __init__(self, db_path: str = "data/memorabilia.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Listings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id TEXT UNIQUE,
                platform TEXT,
                player_name TEXT,
                tier TEXT,
                title TEXT,
                price REAL,
                url TEXT,
                image_url TEXT,
                authentication TEXT,
                cert_number TEXT,
                item_type TEXT,
                inscription TEXT,
                condition TEXT,
                seller TEXT,
                seller_rating REAL,
                end_date TEXT,
                game_used BOOLEAN,
                first_seen TEXT,
                last_updated TEXT,
                status TEXT,
                raw_data TEXT
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                item_type TEXT,
                sale_price REAL,
                sale_date TEXT,
                authentication TEXT,
                inscription BOOLEAN,
                game_used BOOLEAN,
                platform TEXT,
                INDEX idx_player_date (player_name, sale_date)
            )
        ''')
        
        # Scores table (for dashboard prioritization)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listing_scores (
                listing_id TEXT PRIMARY KEY,
                total_score REAL,
                price_score REAL,
                auth_score REAL,
                inscription_score REAL,
                condition_score REAL,
                seller_score REAL,
                calculated_at TEXT,
                FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_listing(self, listing: Dict) -> bool:
        """Add or update a listing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO listings (
                    listing_id, platform, player_name, tier, title, price, url, 
                    image_url, authentication, cert_number, item_type, inscription,
                    condition, seller, seller_rating, end_date, game_used,
                    first_seen, last_updated, status, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing.get('listing_id'),
                listing.get('platform'),
                listing.get('player_name'),
                listing.get('tier'),
                listing.get('title'),
                listing.get('price'),
                listing.get('url'),
                listing.get('image_url'),
                listing.get('authentication'),
                listing.get('cert_number'),
                listing.get('item_type'),
                listing.get('inscription'),
                listing.get('condition'),
                listing.get('seller'),
                listing.get('seller_rating'),
                listing.get('end_date'),
                listing.get('game_used', False),
                listing.get('first_seen', datetime.now().isoformat()),
                datetime.now().isoformat(),
                listing.get('status', 'active'),
                json.dumps(listing.get('raw_data', {}))
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding listing: {e}")
            return False
        finally:
            conn.close()
    
    def add_price_history(self, sale: Dict) -> bool:
        """Add a completed sale to price history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO price_history (
                    player_name, item_type, sale_price, sale_date,
                    authentication, inscription, game_used, platform
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sale.get('player_name'),
                sale.get('item_type'),
                sale.get('sale_price'),
                sale.get('sale_date'),
                sale.get('authentication'),
                sale.get('inscription', False),
                sale.get('game_used', False),
                sale.get('platform')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding price history: {e}")
            return False
        finally:
            conn.close()
    
    def get_average_price(self, player: str, item_type: str = None, 
                         days: int = 90) -> Optional[float]:
        """Get average sale price for a player over specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT AVG(sale_price) FROM price_history
            WHERE player_name = ?
            AND sale_date >= date('now', '-' || ? || ' days')
        '''
        params = [player, days]
        
        if item_type:
            query += ' AND item_type = ?'
            params.append(item_type)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] else None
    
    def get_active_listings(self, tier: str = None, player: str = None) -> List[Dict]:
        """Get all active listings, optionally filtered"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM listings WHERE status = "active"'
        params = []
        
        if tier:
            query += ' AND tier = ?'
            params.append(tier)
        
        if player:
            query += ' AND player_name = ?'
            params.append(player)
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def save_score(self, listing_id: str, scores: Dict):
        """Save calculated scores for a listing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO listing_scores (
                listing_id, total_score, price_score, auth_score,
                inscription_score, condition_score, seller_score, calculated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            listing_id,
            scores.get('total'),
            scores.get('price'),
            scores.get('authentication'),
            scores.get('inscription'),
            scores.get('condition'),
            scores.get('seller'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_top_scored_listings(self, limit: int = 10, tier: str = None) -> List[Dict]:
        """Get highest scored listings for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT l.*, s.total_score, s.price_score, s.auth_score
            FROM listings l
            JOIN listing_scores s ON l.listing_id = s.listing_id
            WHERE l.status = "active"
        '''
        
        if tier:
            query += ' AND l.tier = ?'
            cursor.execute(query + ' ORDER BY s.total_score DESC LIMIT ?', (tier, limit))
        else:
            cursor.execute(query + ' ORDER BY s.total_score DESC LIMIT ?', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return results
