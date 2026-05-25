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
    
    # 2. Hämta data
    url = "https://www.fotmob.com/api/data/leagues?id=67&ccode3=SWE"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.fotmob.com/',
        'Accept': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # 3. Extrahera tabell-data
    table_data = data['table'][0]['data']['table']['all']
    
    # DEBUG: Denna rad skriver ut vad som finns i datan så vi kan se rätt nycklar
    print(f"DEBUG: Data för första laget: {table_data[0]}")
    
    # 4. Förbered rader
    rows = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng"]]
    
    for team in table_data:
        # Här testar vi de vanligaste varianterna på nyckelnamn
        rows.append([
            team.get('idx', ''),
            team.get('name', ''),
            team.get('played', 0),
            team.get('wins', team.get('won', 0)),           # Testar 'wins' eller 'won'
            team.get('draws', team.get('drawn', 0)),        # Testar 'draws' eller 'drawn'
            team.get('losses', team.get('lost', 0)),        # Testar 'losses' eller 'lost'
            team.get('goalsFor', team.get('goalScored', 0)),# Testar 'goalsFor' eller 'goalScored'
            team.get('goalsAgainst', team.get('goalConceded', 0)), # Testar 'goalsAgainst' eller 'goalConceded'
            team.get('goalDifference', 0),
            team.get('pts', 0)
        ])
    
    # 5. Uppdatera Google Sheet
    sheet = client.open("FOTMOB data").worksheet("tabell")
    sheet.clear()
    sheet.update(range_name='A1', values=rows)
    print("Tabellen har uppdaterats!")

if __name__ == "__main__":
    main()
