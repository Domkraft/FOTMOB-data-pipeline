import os
import json
import gspread
import requests
from google.oauth2.service_account import Credentials

def main():
    creds_raw = os.environ.get('GCP_CREDENTIALS')
    if not creds_raw:
        raise ValueError("GCP_CREDENTIALS secret not found!")
    
    creds_dict = json.loads(creds_raw)
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    url = "https://www.fotmob.com/api/data/tltable?leagueId=67"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.fotmob.com/',
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # DEBUG: Eftersom data är en lista, skriv ut vad det första elementet är
    if isinstance(data, list) and len(data) > 0:
        print(f"DEBUG: Första elementet i listan: {json.dumps(data[0], indent=2)[:1000]}")
    else:
        print(f"DEBUG: Data är inte en lista eller är tom: {type(data)}")

if __name__ == "__main__":
    main()
