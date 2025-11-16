import json
from datetime import datetime
from typing import List, Dict
from database import MemorabiliaDatabase
import matplotlib.pyplot as plt
import base64
from io import BytesIO

class DashboardGenerator:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.db = MemorabiliaDatabase()
    
    def generate_dashboard(self, output_path: str = "data/dashboard.html"):
        """Generate complete HTML dashboard"""
        print("Generating dashboard...")
        
        html = self._build_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Dashboard saved to {output_path}")
        return output_path
    
    def _build_html(self) -> str:
        """Build complete HTML document"""
        sections = self.config['dashboard_sections']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Memorabilia Finds - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏆 Bay Area Sports Memorabilia Tracker</h1>
            <p class="date">{datetime.now().strftime('%A, %B %d, %Y')}</p>
        </header>
        
        {self._build_priority_alerts() if 'priority_alerts' in sections else ''}
        {self._build_inscribed_championship() if 'inscribed_championship' in sections else ''}
        {self._build_game_used() if 'game_used' in sections else ''}
        {self._build_signed_items() if 'signed_balls_photos' in sections else ''}
        {self._build_dynasty_items() if 'dynasty_team_items' in sections else ''}
        {self._build_golf_section() if 'golf_section' in sections else ''}
        {self._build_market_intelligence() if 'market_intelligence' in sections else ''}
    </div>
</body>
</html>
"""
        return html
    
    def _get_css(self) -> str:
        """Return CSS styles"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .date {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #1a1a2e;
            border-bottom: 3px solid #ffa500;
            padding-bottom: 10px;
        }
        
        .alert-badge {
            display: inline-block;
            background: #ff4444;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-left: 10px;
        }
        
        .item-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .item-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .item-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        
        .item-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
            background: #f0f0f0;
        }
        
        .item-content {
            padding: 15px;
        }
        
        .item-title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #1a1a2e;
            line-height: 1.4;
        }
        
        .item-price {
            font-size: 1.5em;
            font-weight: 700;
            color: #27ae60;
            margin-bottom: 10px;
        }
        
        .item-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .badge-auth {
            background: #3498db;
            color: white;
        }
        
        .badge-inscription {
            background: #9b59b6;
            color: white;
        }
        
        .badge-game-used {
            background: #e74c3c;
            color: white;
        }
        
        .badge-player {
            background: #34495e;
            color: white;
        }
        
        .score-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #f39c12 0%, #27ae60 100%);
            transition: width 0.3s;
        }
        
        .score-text {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 12px;
        }
        
        .item-link {
            display: block;
            text-align: center;
            background: #ffa500;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }
        
        .item-link:hover {
            background: #ff8c00;
        }
        
        .inscription-text {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
            font-style: italic;
            font-size: 0.95em;
        }
        
        .price-trend {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: 700;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 5px;
        }
        
        .no-items {
            text-align: center;
            padding: 40px;
            color: #95a5a6;
            font-size: 1.1em;
        }
        
        .ending-soon {
            background: #fee;
            border-left: 4px solid #e74c3c;
            padding: 8px 12px;
            margin-top: 8px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: 600;
            color: #c0392b;
        }
        """
    
    def _build_priority_alerts(self) -> str:
        """Build priority alerts section for Tier 1 investment pieces"""
        top_listings = self.db.get_top_scored_listings(limit=10, tier='tier1')
        
        if not top_listings:
            return f"""
            <div class="section">
                <h2 class="section-title">🔔 PRIORITY ALERTS - Investment Grade</h2>
                <p class="no-items">No high-value opportunities found today</p>
            </div>
            """
        
        items_html = ""
        for listing in top_listings:
            items_html += self._build_item_card(listing, show_score=True)
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                🔔 PRIORITY ALERTS - Investment Grade
                <span class="alert-badge">{len(top_listings)} items</span>
            </h2>
            <div class="item-grid">
                {items_html}
            </div>
        </div>
        """
    
    def _build_inscribed_championship(self) -> str:
        """Build inscribed championship items section"""
        all_listings = self.db.get_active_listings()
        
        # Filter for inscribed championship items
        inscribed = [l for l in all_listings 
                    if l.get('inscription') and 
                    any(term in str(l.get('inscription', '')).lower() 
                        for term in ['champ', 'world series', 'nba', 'super bowl', 'finals'])]
        
        # Sort by score
        inscribed_ids = [l['listing_id'] for l in inscribed]
        scored_listings = [l for l in self.db.get_top_scored_listings(limit=100) 
                          if l['listing_id'] in inscribed_ids]
        
        if not scored_listings:
            return ""
        
        items_html = ""
        for listing in scored_listings[:10]:
            items_html += self._build_item_card(listing)
        
        return f"""
        <div class="section">
            <h2 class="section-title">🏆 Championship Inscribed Items</h2>
            <div class="item-grid">
                {items_html}
            </div>
        </div>
        """
    
    def _build_game_used(self) -> str:
        """Build game-used memorabilia section"""
        all_listings = self.db.get_active_listings()
        game_used = [l for l in all_listings if l.get('game_used')]
        
        if not game_used:
            return ""
        
        # Get scores
        game_used_ids = [l['listing_id'] for l in game_used]
        scored_listings = [l for l in self.db.get_top_scored_listings(limit=100) 
                          if l['listing_id'] in game_used_ids]
        
        items_html = ""
        for listing in scored_listings[:10]:
            items_html += self._build_item_card(listing)
        
        return f"""
        <div class="section">
            <h2 class="section-title">👕 Game-Used & Game-Worn</h2>
            <div class="item-grid">
                {items_html}
            </div>
        </div>
        """
    
    def _build_signed_items(self) -> str:
        """Build signed balls and photos section"""
        all_listings = self.db.get_active_listings()
        signed_items = [l for l in all_listings 
                       if l.get('item_type') in ['ball', 'photo']]
        
        if not signed_items:
            return ""
        
        signed_ids = [l['listing_id'] for l in signed_items]
        scored_listings = [l for l in self.db.get_top_scored_listings(limit=100) 
                          if l['listing_id'] in signed_ids]
        
        items_html = ""
        for listing in scored_listings[:12]:
            items_html += self._build_item_card(listing)
        
        return f"""
        <div class="section">
            <h2 class="section-title">⚾ Signed Balls & Photos</h2>
            <div class="item-grid">
                {items_html}
            </div>
        </div>
        """
    
    def _build_dynasty_items(self) -> str:
        """Build dynasty team items section"""
        all_listings = self.db.get_active_listings()
        dynasty_items = [l for l in all_listings 
                        if any(term in str(l.get('title', '')).lower() + str(l.get('inscription', '')).lower()
                              for term in ['dynasty', 'even year', 'splash brothers', '2010', '2012', '2014', '2015', '2017', '2018'])]
        
        if not dynasty_items:
            return ""
        
        dynasty_ids = [l['listing_id'] for l in dynasty_items]
        scored_listings = [l for l in self.db.get_top_scored_listings(limit=100) 
                          if l['listing_id'] in dynasty_ids]
        
        items_html = ""
        for listing in scored_listings[:10]:
            items_html += self._build_item_card(listing)
        
        return f"""
        <div class="section">
            <h2 class="section-title">🌟 Dynasty & Championship Teams</h2>
            <div class="item-grid">
                {items_html}
            </div>
        </div>
        """
    
    def _build_golf_section(self) -> str:
        """Build golf memorabilia section"""
        golf_listings = self.db.get_active_listings(tier='golf')
        
        if not golf_listings:
            return ""
        
        golf_ids = [l['listing_id'] for l in golf_listings]
        scored_listings = [l for l in self.db.get_top_scored_listings(limit=100) 
                          if l['listing_id'] in golf_ids]
        
        items_html = ""
        for listing in scored_listings[:10]:
            items_html += self._build_item_card(listing)
        
        return f"""
        <div class="section">
            <h2 class="section-title">⛳ Golf - Tiger Woods & Scottie Scheffler</h2>
            <div class="item-grid">
                {items_html}
            </div>
        </div>
        """
    
    def _build_market_intelligence(self) -> str:
        """Build market intelligence section with stats and trends"""
        all_listings = self.db.get_active_listings()
        
        total_items = len(all_listings)
        tier1_count = len([l for l in all_listings if l.get('tier') == 'tier1'])
        inscribed_count = len([l for l in all_listings if l.get('inscription')])
        game_used_count = len([l for l in all_listings if l.get('game_used')])
        
        return f"""
        <div class="section">
            <h2 class="section-title">📊 Market Intelligence</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_items}</div>
                    <div class="stat-label">Active Listings</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tier1_count}</div>
                    <div class="stat-label">Investment Grade</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{inscribed_count}</div>
                    <div class="stat-label">Inscribed Items</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{game_used_count}</div>
                    <div class="stat-label">Game-Used</div>
                </div>
            </div>
        </div>
        """
    
    def _build_item_card(self, listing: Dict, show_score: bool = False) -> str:
        """Build HTML for a single item card"""
        badges = []
        
        if listing.get('authentication'):
            badges.append(f'<span class="badge badge-auth">{listing["authentication"]}</span>')
        
        if listing.get('inscription'):
            badges.append(f'<span class="badge badge-inscription">Inscribed</span>')
        
        if listing.get('game_used'):
            badges.append(f'<span class="badge badge-game-used">Game Used</span>')
        
        badges.append(f'<span class="badge badge-player">{listing.get("player_name", "Unknown")}</span>')
        
        badges_html = ' '.join(badges)
        
        inscription_html = ""
        if listing.get('inscription'):
            inscription_html = f'<div class="inscription-text">"{listing["inscription"]}"</div>'
        
        score_html = ""
        if show_score:
            score = listing.get('total_score', 0)
            score_html = f'''
            <div class="score-bar">
                <div class="score-fill" style="width: {score}%"></div>
            </div>
            <div class="score-text">Value Score: {score}/100</div>
            '''
        
        ending_soon_html = ""
        if listing.get('end_date'):
            try:
                end_date = datetime.fromisoformat(listing['end_date'])
                hours_left = (end_date - datetime.now()).total_seconds() / 3600
                if hours_left < 24:
                    ending_soon_html = f'<div class="ending-soon">⏰ Ends in {int(hours_left)} hours</div>'
            except:
                pass
        
        image_url = listing.get('image_url', '')
        if not image_url:
            image_url = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f0f0f0" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E'
        
        return f"""
        <div class="item-card">
            <img class="item-image" src="{image_url}" alt="{listing.get('title', 'Item')}" loading="lazy">
            <div class="item-content">
                <div class="item-title">{listing.get('title', 'Unknown Item')[:100]}</div>
                <div class="item-price">${listing.get('price', 0):,.2f}</div>
                <div class="item-meta">
                    {badges_html}
                </div>
                {inscription_html}
                {score_html}
                {ending_soon_html}
                <a href="{listing.get('url', '#')}" target="_blank" class="item-link">View Listing →</a>
            </div>
        </div>
        """

if __name__ == "__main__":
    generator = DashboardGenerator()
    generator.generate_dashboard()
