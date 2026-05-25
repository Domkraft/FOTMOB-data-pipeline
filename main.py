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
    
    # DEBUG: Skriv ut strukturen för att hitta tabellen
    print(f"DEBUG: Data keys: {list(data.keys())}")
    
    # Om 'table' inte är en lista med index, kanske det är en direkt nyckel?
    # Vi behöver se vad 'data' innehåller.
    
    # (Vi avbryter här för att du ska kunna se debug-loggen)
    print("DEBUG: Skriptet pausat för att inspektera loggen.")

if __name__ == "__main__":
    main()
