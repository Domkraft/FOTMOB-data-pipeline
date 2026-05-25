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
    
    # 2. Hämta data från Fotmob med korrekta headers
    # Vi använder en URL som är mer standardiserad för deras interna API-anrop
    url = "https://www.fotmob.com/api/leagues?id=67"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.fotmob.com/leagues/67/overview/allsvenskan',
        'Accept': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Fel: Kunde inte hämta data (Status {response.status_code})")
        return
    
    data = response.json()
    
    # 3. Extrahera tabell-data
    # Vi behöver verifiera strukturen
    try:
        table_data = data['table'][0]['data']['table']['all']
    except (KeyError, IndexError) as e:
        print(f"Kunde inte hitta tabell i svaret. Fel: {e}")
        return
    
    # 4. Förbered rader
    rows = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng"]]
    for team in table_data:
        rows.append([
            team.get('idx', ''),
            team.get('name', ''),
            team.get('played', 0),
            team.get('won', 0),
            team.get('drawn', 0),
            team.get('lost', 0),
            team.get('goalScored', 0),
            team.get('goalConceded', 0),
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
