import json
from typing import Dict, Optional
from database import MemorabiliaDatabase

class ListingAnalyzer:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.db = MemorabiliaDatabase()
        self.weights = self.config['scoring_weights']
    
    def analyze_all_listings(self):
        """Analyze and score all active listings"""
        print("Analyzing listings...")
        
        active_listings = self.db.get_active_listings()
        
        for listing in active_listings:
            scores = self.calculate_scores(listing)
            self.db.save_score(listing['listing_id'], scores)
        
        print(f"Analyzed {len(active_listings)} listings")
    
    def calculate_scores(self, listing: Dict) -> Dict:
        """Calculate all scores for a listing"""
        scores = {
            'price': self._score_price(listing),
            'authentication': self._score_authentication(listing),
            'inscription': self._score_inscription(listing),
            'condition': self._score_condition(listing),
            'seller': self._score_seller(listing)
        }
        
        # Calculate weighted total
        total = 0
        for category, score in scores.items():
            weight = self.weights.get(f"{category}_{'vs_average' if category == 'price' else 'quality'}", 0)
            total += score * (weight / 100)
        
        scores['total'] = round(total, 2)
        
        return scores
    
    def _score_price(self, listing: Dict) -> float:
        """Score based on price vs historical average (0-100)"""
        price = listing.get('price', 0)
        
        if price == 0:
            return 0
        
        # Get historical average
        avg_price = self.db.get_average_price(
            listing['player_name'],
            listing.get('item_type'),
            days=90
        )
        
        if not avg_price or avg_price == 0:
            # No historical data - score based on absolute price for tier
            tier = listing.get('tier')
            if tier == 'tier1':
                # For tier 1, lower absolute prices score higher
                if price < 500:
                    return 90
                elif price < 1000:
                    return 70
                elif price < 2000:
                    return 50
                else:
                    return 30
            else:
                # For tier 2, score relative to max
                max_price = self.config.get(f'{tier}_players', {}).get('price_max', 500)
                if price < max_price * 0.5:
                    return 90
                elif price < max_price * 0.75:
                    return 70
                elif price < max_price:
                    return 50
                else:
                    return 20
        
        # Score based on percentage below average
        percentage_below = ((avg_price - price) / avg_price) * 100
        
        if percentage_below >= 40:
            return 100
        elif percentage_below >= 30:
            return 90
        elif percentage_below >= 20:
            return 80
        elif percentage_below >= 10:
            return 70
        elif percentage_below >= 0:
            return 60
        elif percentage_below >= -10:
            return 40
        elif percentage_below >= -20:
            return 20
        else:
            return 10
    
    def _score_authentication(self, listing: Dict) -> float:
        """Score authentication quality (0-100)"""
        auth = listing.get('authentication', '').upper()
        
        if not auth:
            return 10  # No authentication
        
        # Tier authentication services
        top_tier = ['PSA', 'JSA', 'JAMES SPENCE', 'BAS', 'BECKETT']
        mid_tier = ['FANATICS', 'STEINER', 'MLB', 'NFL', 'PGA', 'UPPER DECK']
        low_tier = ['TRISTAR']
        
        for service in top_tier:
            if service in auth:
                return 100
        
        for service in mid_tier:
            if service in auth:
                return 75
        
        for service in low_tier:
            if service in auth:
                return 50
        
        return 25  # Unknown authentication
    
    def _score_inscription(self, listing: Dict) -> float:
        """Score inscription value (0-100)"""
        inscription = listing.get('inscription')
        
        if not inscription:
            return 20  # No inscription
        
        inscription_lower = inscription.lower()
        
        # Championship inscriptions (highest value)
        champ_patterns = self.config['inscription_patterns']['championships']
        if any(pattern.lower() in inscription_lower for pattern in champ_patterns):
            return 100
        
        # Award inscriptions (high value)
        award_patterns = self.config['inscription_patterns']['awards']
        if any(pattern.lower() in inscription_lower for pattern in award_patterns):
            return 90
        
        # Record inscriptions (high value)
        record_patterns = self.config['inscription_patterns']['records']
        if any(pattern.lower() in inscription_lower for pattern in record_patterns):
            return 85
        
        # Dynasty/team inscriptions (medium value)
        dynasty_patterns = self.config['inscription_patterns']['dynasties']
        if any(pattern.lower() in inscription_lower for pattern in dynasty_patterns):
            return 75
        
        # Achievement inscriptions (medium value)
        achievement_patterns = self.config['inscription_patterns']['achievements']
        if any(pattern.lower() in inscription_lower for pattern in achievement_patterns):
            return 70
        
        # Generic inscription
        return 40
    
    def _score_condition(self, listing: Dict) -> float:
        """Score item condition (0-100)"""
        condition = listing.get('condition', '').lower()
        game_used = listing.get('game_used', False)
        
        # Game used items score high regardless of condition
        if game_used:
            return 95
        
        if not condition:
            return 50  # Unknown condition
        
        if 'mint' in condition or 'nm' in condition:
            return 100
        elif 'excellent' in condition or 'ex' in condition:
            return 90
        elif 'very good' in condition or 'vg' in condition:
            return 75
        elif 'good' in condition:
            return 60
        elif 'fair' in condition:
            return 40
        elif 'poor' in condition:
            return 20
        
        return 50
    
    def _score_seller(self, listing: Dict) -> float:
        """Score seller reputation (0-100)"""
        seller_rating = listing.get('seller_rating')
        
        if not seller_rating:
            return 50  # Unknown seller
        
        # Convert to percentage score
        if seller_rating >= 99.5:
            return 100
        elif seller_rating >= 99:
            return 90
        elif seller_rating >= 98:
            return 75
        elif seller_rating >= 95:
            return 60
        elif seller_rating >= 90:
            return 40
        else:
            return 20

if __name__ == "__main__":
    analyzer = ListingAnalyzer()
    analyzer.analyze_all_listings()
