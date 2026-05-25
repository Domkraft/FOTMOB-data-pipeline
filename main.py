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
    
    spreadsheet = client.open("FOTMOB data")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 2. Hämta data från den endpoint som vi VET fungerar
    url = "https://www.fotmob.com/api/data/tltable?leagueId=67"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # --- UPPDATERA TABELL ---
    table_data = data[0]['data']['table']['all']
    rows_table = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng", "PPM"]]
    
    for team in table_data:
        goals_str = team.get('scoresStr', '0-0')
        goals_list = goals_str.split('-')
        gjorda = goals_list[0] if len(goals_list) > 0 else 0
        inslappta = goals_list[1] if len(goals_list) > 1 else 0
        played = team.get('played', 0)
        pts = team.get('pts', 0)
        ppm = round(pts / played, 2) if played > 0 else 0
        
        rows_table.append([
            team.get('idx', ''), team.get('name', ''), played, team.get('wins', 0),
            team.get('draws', 0), team.get('losses', 0), gjorda, inslappta,
            team.get('goalConDiff', 0), pts, ppm
        ])
    
    sheet_table = spreadsheet.worksheet("tabell")
    sheet_table.clear()
    sheet_table.update(range_name='A1', values=rows_table)
    
    # --- UPPDATERA MATCHER ---
    # Vi hämtar matchdata från samma data-objekt om möjligt, 
    # annars faller vi tillbaka på att bara skriva ut att data saknas
    matches = data[0]['data'].get('matches', [])
    rows_matches = [["Datum/Tid", "Omgång", "Hemmalag", "Bortalag", "Hemmalagsmål", "Bortalagsmål"]]
    
    for m in matches:
        home = m.get('home', {})
        away = m.get('away', {})
        rows_matches.append([
            m.get('status', {}).get('utcTime', ''),
            m.get('round', ''),
            home.get('name', ''),
            away.get('name', ''),
            home.get('score', 0) if home.get('score') is not None else 0,
            away.get('score', 0) if away.get('score') is not None else 0
        ])
    
    sheet_matches = spreadsheet.worksheet("matcher")
    sheet_matches.clear()
    sheet_matches.update(range_name='A1', values=rows_matches)
    
    print("Tabell och matcher uppdaterade via tltable-endpointen!")

if __name__ == "__main__":
    main()
