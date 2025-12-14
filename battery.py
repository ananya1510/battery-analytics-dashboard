import requests
import json
from typing import Optional, Dict, List
from datetime import datetime

class BatteryAPI:
    """Client for accessing Battery Cycle Data API"""
    
    def __init__(self, base_url: str):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_summary(self, imei: Optional[str] = None) -> Dict:
        """
        Get summary of all accessible batteries
        
        Args:
            imei: Optional IMEI filter
            
        Returns:
            Dictionary containing summary data
        """
        url = f"{self.base_url}/api/snapshots/summary"
        params = {}
        if imei:
            params['imei'] = imei
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching summary: {e}")
            return {}
    
    def get_snapshots(self, imei: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get cycle snapshots for a specific battery
        
        Args:
            imei: Battery IMEI (required)
            limit: Number of records to fetch (default 100)
            offset: Starting position (default 0)
            
        Returns:
            List of cycle snapshot dictionaries
        """
        url = f"{self.base_url}/api/snapshots"
        params = {
            'imei': imei,
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching snapshots: {e}")
            return []
    
    def get_latest_snapshot(self, imei: str) -> Dict:
        """
        Get the most recent cycle snapshot for a battery
        
        Args:
            imei: Battery IMEI
            
        Returns:
            Dictionary containing the latest snapshot
        """
        url = f"{self.base_url}/api/snapshots/{imei}/latest"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching latest snapshot: {e}")
            return {}
    
    def get_cycle_details(self, imei: str, cycle_number: int) -> Dict:
        """
        Get detailed analytics for a specific cycle
        
        Args:
            imei: Battery IMEI
            cycle_number: Cycle number to retrieve
            
        Returns:
            Dictionary containing cycle details
        """
        url = f"{self.base_url}/api/snapshots/{imei}/cycles/{cycle_number}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching cycle details: {e}")
            return {}
    
    def fetch_all_snapshots(self, imei: str, batch_size: int = 100) -> List[Dict]:
        """
        Fetch all available snapshots for a battery (handles pagination)
        
        Args:
            imei: Battery IMEI
            batch_size: Number of records per request
            
        Returns:
            List of all cycle snapshots
        """
        all_snapshots = []
        offset = 0
        
        while True:
            batch = self.get_snapshots(imei, limit=batch_size, offset=offset)
            
            if not batch:
                break
            
            all_snapshots.extend(batch)
            
            # Check if we got fewer records than requested (end of data)
            if len(batch) < batch_size:
                break
            
            offset += batch_size
            print(f"Fetched {len(all_snapshots)} snapshots so far...")
        
        return all_snapshots


def main():
    """Main function demonstrating API usage"""
    
    # Configuration
    BASE_URL = "https://zenfinity-intern-api-104290304048.europe-west1.run.app"
    AUTHORIZED_IMEIS = [
        "865044073967657",
        "865044073949366"
    ]
    
    # Initialize API client
    api = BatteryAPI(BASE_URL)
    
    # Part 1: Get summary data
    print("=" * 60)
    print("FETCHING SUMMARY DATA")
    print("=" * 60)
    summary = api.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Select first authorized IMEI
    selected_imei = AUTHORIZED_IMEIS[0]
    print(f"\n{'=' * 60}")
    print(f"SELECTED IMEI: {selected_imei}")
    print("=" * 60)
    
    # Get latest snapshot
    print("\nFetching latest snapshot...")
    latest = api.get_latest_snapshot(selected_imei)
    print(json.dumps(latest, indent=2))
    
    # Get detailed cycle snapshots
    print(f"\n{'=' * 60}")
    print("FETCHING CYCLE SNAPSHOTS")
    print("=" * 60)
    snapshots = api.get_snapshots(selected_imei, limit=10)
    print(f"Retrieved {len(snapshots)} snapshots")
    
    if snapshots:
        print("\nFirst snapshot:")
        print(json.dumps(snapshots[0], indent=2))
        
        # Get specific cycle details if available
        if 'cycle_number' in snapshots[0]:
            cycle_num = snapshots[0]['cycle_number']
            print(f"\n{'=' * 60}")
            print(f"FETCHING CYCLE {cycle_num} DETAILS")
            print("=" * 60)
            cycle_details = api.get_cycle_details(selected_imei, cycle_num)
            print(json.dumps(cycle_details, indent=2))
    
    # Optional: Fetch all snapshots (uncomment if needed)
    print("\nFetching all snapshots (this may take a while)...")
    all_snapshots = api.fetch_all_snapshots(selected_imei)
    print(f"Total snapshots retrieved: {len(all_snapshots)}")
    
    # Save data to file
    output_file = f"battery_data_{selected_imei}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'summary': summary,
            'latest_snapshot': latest,
            'recent_snapshots': snapshots
        }, f, indent=2)
    print(f"\nData saved to: {output_file}")


if __name__ == "__main__":
    main()