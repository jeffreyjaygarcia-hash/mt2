#!/usr/bin/env python3
"""
Main runner script for the Memorabilia Tracker
Orchestrates scraping, analysis, and dashboard generation
"""

import os
import sys
from datetime import datetime
from scraper import MemorabilliaScraper
from analyzer import ListingAnalyzer
from dashboard_generator import DashboardGenerator

def main():
    """Main execution function"""
    print(f"\n{'='*60}")
    print(f"Bay Area Sports Memorabilia Tracker")
    print(f"Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    try:
        # Step 1: Scrape all platforms
        print("STEP 1: Scraping listings...")
        scraper = MemorabilliaScraper()
        scraper.scrape_all()
        print("✓ Scraping complete\n")
        
        # Step 2: Analyze and score listings
        print("STEP 2: Analyzing listings...")
        analyzer = ListingAnalyzer()
        analyzer.analyze_all_listings()
        print("✓ Analysis complete\n")
        
        # Step 3: Generate dashboard
        print("STEP 3: Generating dashboard...")
        generator = DashboardGenerator()
        dashboard_path = generator.generate_dashboard()
        print(f"✓ Dashboard generated: {dashboard_path}\n")
        
        print(f"{'='*60}")
        print(f"✓ ALL TASKS COMPLETED SUCCESSFULLY")
        print(f"Run finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
