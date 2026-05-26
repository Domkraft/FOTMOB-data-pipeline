import os
import json
import gspread
import requests
import pandas as pd
from io import StringIO
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
    
    # 2. Uppdatera tabell (FotMob)
    url_table = "https://www.fotmob.com/api/data/tltable?leagueId=67"
    response_table = requests.get(url_table, headers=headers)
    data_table = response_table.json()
    
    table_data = data_table[0]['data']['table']['all']
    rows_table = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng", "PPM"]]
    
    for team in table_data:
        played = team.get('played', 0)
        pts = team.get('pts', 0)
        ppm = round(float(pts) / float(played), 2) if played > 0 else 0.0
        
        rows_table.append([
            team.get('idx', ''), team.get('name', ''), played, team.get('wins', 0),
            team.get('draws', 0), team.get('losses', 0), 
            team.get('scoresStr', '0-0').split('-')[0], 
            team.get('scoresStr', '0-0').split('-')[1],
            team.get('goalConDiff', 0), pts, ppm
        ])
    
    # Uppdatera tabellfliken utan att rensa hela arket
    sheet_table = spreadsheet.worksheet("tabell")
    sheet_table.batch_clear(['A1:K50']) 
    sheet_table.update(range_name='A1', values=rows_table)
    
    # 3. Uppdatera matcher från CSV
    url_csv = "https://www.football-data.co.uk/new/SWE.csv"
    response_csv = requests.get(url_csv)
    df = pd.read_csv(StringIO(response_csv.text))
    
    # Konvertera datum
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['År'] = df['Date'].dt.year
    df['Datum'] = df['Date'].dt.strftime('%m-%d')
    
    # Använd exakta namn från bilden
    df_clean = df[['År', 'Datum', 'Home', 'Away', 'HG', 'AG']].copy()
    df_clean.columns = ["År", "Datum", "Hemmalag", "Bortalag", "Hemmalagsmål", "Bortalagsmål"]
    
    # Skriv till arket
    rows_matches = [df_clean.columns.tolist()] + df_clean.values.tolist()
    
    # Uppdatera matcherfliken utan att rensa hela arket
    sheet_matches = spreadsheet.worksheet("matcher")
    sheet_matches.batch_clear(['A1:G1000'])
    sheet_matches.update(range_name='A1', values=rows_matches)
    
    print("Tabell och matcher har uppdaterats, övrig data i arket bevarad!")

if __name__ == "__main__":
    main()