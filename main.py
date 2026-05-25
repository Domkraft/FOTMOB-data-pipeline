import os
import json
import gspread
import requests
from google.oauth2.service_account import Credentials

def main():
    # 1. Autentisering
    creds_raw = os.environ.get('GCP_CREDENTIALS')
    if not creds_raw:
        raise ValueError("GCP_CREDENTIALS secret not found!")
    
    creds_dict = json.loads(creds_raw)
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    # 2. Hämta data från den specifika tltable-endpointen
    url = "https://www.fotmob.com/api/data/tltable?leagueId=67"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.fotmob.com/',
        'Accept': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # 3. Extrahera tabell-data
    # tltable returnerar tabellen direkt i ett annat format
    table_data = data['table'][0]['data']['table']['all']
    
    # DEBUG: Printa ett lag för att se de exakta xG-nycklarna
    print(f"DEBUG: Lagobjekt från tltable: {table_data[0]}")
    
    # 4. Förbered rader med xG och xGA
    # Notera att vi lägger till kolumner för xG och xGA
    rows = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng", "xG", "xGA"]]
    
    for team in table_data:
        goals_str = team.get('scoresStr', '0-0')
        goals_list = goals_str.split('-')
        gjorda = goals_list[0] if len(goals_list) > 0 else 0
        inslappta = goals_list[1] if len(goals_list) > 1 else 0
        
        rows.append([
            team.get('idx', ''),
            team.get('name', ''),
            team.get('played', 0),
            team.get('wins', 0),
            team.get('draws', 0),
            team.get('losses', 0),
            gjorda,
            inslappta,
            team.get('goalConDiff', 0),
            team.get('pts', 0),
            team.get('expectedGoals', 0),  # Försöker hämta xG
            team.get('expectedGoalsAgainst', 0) # Försöker hämta xGA
        ])
    
    # 5. Uppdatera Google Sheet
    sheet = client.open("FOTMOB data").worksheet("tabell")
    sheet.clear()
    sheet.update(range_name='A1', values=rows)
    print("Tabellen har uppdaterats med xG-data!")

if __name__ == "__main__":
    main()
