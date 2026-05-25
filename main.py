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
    
    # 2. Hämta och uppdatera tabellen
    url_table = "https://www.fotmob.com/api/data/tltable?leagueId=67"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response_table = requests.get(url_table, headers=headers)
    data_table = response_table.json()
    
    table_data = data_table[0]['data']['table']['all']
    rows_table = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng", "xG", "xGA"]]
    
    for team in table_data:
        goals_str = team.get('scoresStr', '0-0')
        goals_list = goals_str.split('-')
        gjorda = goals_list[0] if len(goals_list) > 0 else 0
        inslappta = goals_list[1] if len(goals_list) > 1 else 0
        
        rows_table.append([
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
            team.get('expectedGoals', 0),
            team.get('expectedGoalsAgainst', 0)
        ])
    
    spreadsheet = client.open("FOTMOB data")
    sheet_table = spreadsheet.worksheet("tabell")
    sheet_table.clear()
    sheet_table.update(range_name='A1', values=rows_table)
    
    # 3. Hämta och uppdatera matcher
    url_matches = "https://www.fotmob.com/api/data/leagues?id=67&type=matches&ccode3=SWE"
    response_matches = requests.get(url_matches, headers=headers)
    data_matches = response_matches.json()
    
    matches = data_matches.get('matches', {}).get('allMatches', [])
    rows_matches = [["Datum/Tid", "Omgång", "Hemmalag", "Bortalag", "Hemmalagsmål", "Bortalagsmål"]]
    
    for m in matches:
        status = m.get('status', {})
        home = m.get('home', {})
        away = m.get('away', {})
        
        rows_matches.append([
            status.get('utcTime', ''),
            m.get('round', ''),
            home.get('name', ''),
            away.get('name', ''),
            home.get('score', 0) if home.get('score') is not None else 0,
            away.get('score', 0) if away.get('score') is not None else 0
        ])
    
    # Uppdatera fliken 'matcher' (notera litet 'm')
    sheet_matches = spreadsheet.worksheet("matcher")
    sheet_matches.clear()
    sheet_matches.update(range_name='A1', values=rows_matches)
    
    print("Både 'tabell' och 'matcher' har uppdaterats!")

if __name__ == "__main__":
    main()
