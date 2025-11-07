"""
National Parks Data Collector for Google Colab
Fetches park data from the NPS API and writes to Google Sheets
"""

# Import required libraries
import requests
import pandas as pd
import gspread
from google.colab import auth
from google.auth import default

# =============================================================================
# CONFIGURATION - PASTE YOUR VALUES HERE
# =============================================================================

# PASTE YOUR NPS API KEY HERE (get one from https://www.nps.gov/subjects/developer/get-started.htm)
API_KEY = "YOUR_API_KEY_HERE"

# PASTE YOUR GOOGLE SHEET URL HERE (must be a new/empty sheet or existing sheet you want to overwrite)
SHEET_URL = "YOUR_GOOGLE_SHEET_URL_HERE"

# =============================================================================
# DO NOT EDIT BELOW THIS LINE
# =============================================================================

def authenticate_google():
    """Authenticate with Google using Colab auth"""
    print("🔐 Authenticating with Google...")
    auth.authenticate_user()
    creds, _ = default()
    gc = gspread.authorize(creds)
    print("✅ Google authentication successful!")
    return gc

def fetch_parks_data(api_key, limit=50):
    """Fetch parks data from NPS API"""
    print(f"📡 Fetching up to {limit} parks from NPS API...")

    url = "https://developer.nps.gov/api/v1/parks"
    params = {
        "api_key": api_key,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("✅ API request successful!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from NPS API: {e}")
        return None

def parse_parks_data(api_response):
    """Extract relevant park information from API response"""
    print("📊 Parsing park data...")

    if not api_response or "data" not in api_response:
        print("❌ No data found in API response")
        return None

    parks_list = []
    parks_data = api_response["data"]

    for park in parks_data:
        park_info = {
            "fullName": park.get("fullName", "N/A"),
            "states": park.get("states", "N/A"),
            "description": park.get("description", "N/A"),
            "acres": park.get("acres", "N/A"),
            "designation": park.get("designation", "N/A")
        }
        parks_list.append(park_info)

    print(f"✅ Parsed {len(parks_list)} parks successfully!")
    return parks_list

def create_dataframe(parks_list):
    """Create pandas DataFrame from parks list"""
    print("📋 Creating DataFrame...")

    if not parks_list:
        print("❌ No parks data to create DataFrame")
        return None

    df = pd.DataFrame(parks_list)
    print(f"✅ DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    return df

def write_to_google_sheet(gc, sheet_url, df):
    """Write DataFrame to Google Sheet"""
    print("📝 Writing data to Google Sheet...")

    try:
        # Open the sheet
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)  # Use first worksheet

        # Clear existing data
        worksheet.clear()

        # Write headers and data
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

        print(f"✅ Successfully wrote {len(df)} parks to Google Sheet!")
        print(f"🔗 View your data: {sheet_url}")
        return True
    except Exception as e:
        print(f"❌ Error writing to Google Sheet: {e}")
        return False

def main():
    """Main execution function"""
    print("=" * 60)
    print("National Parks Data Collector")
    print("=" * 60)

    # Validate configuration
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ERROR: Please paste your NPS API key in the API_KEY variable")
        return

    if SHEET_URL == "YOUR_GOOGLE_SHEET_URL_HERE":
        print("❌ ERROR: Please paste your Google Sheet URL in the SHEET_URL variable")
        return

    # Step 1: Authenticate with Google
    gc = authenticate_google()
    if not gc:
        return

    # Step 2: Fetch parks data
    api_response = fetch_parks_data(API_KEY, limit=50)
    if not api_response:
        return

    # Step 3: Parse the data
    parks_list = parse_parks_data(api_response)
    if not parks_list:
        return

    # Step 4: Create DataFrame
    df = create_dataframe(parks_list)
    if df is None:
        return

    # Step 5: Write to Google Sheet
    success = write_to_google_sheet(gc, SHEET_URL, df)

    if success:
        print("\n" + "=" * 60)
        print("✅ ALL DONE! Your National Parks data is now in Google Sheets!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Process completed with errors. Please check the messages above.")
        print("=" * 60)

# Run the script
if __name__ == "__main__":
    main()
