import os
import json
import gspread
import requests
from google.oauth2.service_account import Credentials

def main():
    # 1. Autentisering
    creds_dict = json.loads(os.environ['GCP_CREDENTIALS'])
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    # 2. Hämta data från Fotmob (Allsvenskan ID 67)
    url = "https://www.fotmob.com/api/leagues?id=67"
    response = requests.get(url)
    data = response.json()
    
    # Extrahera tabell-data
    table_data = data['table'][0]['data']['table']['all']
    
    # --- DIAGNOS: Printa nycklar för att se vad mer som finns ---
    print("--- DIAGNOS: Tillgängliga nycklar i tabell-objektet ---")
    print(table_data[0].keys())
    print("-------------------------------------------------------")
    
    # 3. Förbered rader för Google Sheets
    rows = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng"]]
    
    for team in table_data:
        rows.append([
            team.get('idx', ''),          # Position
            team.get('name', ''),         # Lag
            team.get('played', 0),        # Spelade
            team.get('won', 0),           # Vinster
            team.get('drawn', 0),         # Oavgjorda
            team.get('lost', 0),          # Förluster
            team.get('goalScored', 0),    # Gjorda mål
            team.get('goalConceded', 0),  # Insläppta mål
            team.get('goalDifference', 0),# Målskillnad
            team.get('pts', 0)            # Poäng
        ])
    
    # 4. Uppdatera Google Sheet
    # OBS: Ersätt "Ditt_Google_Sheet_Namn" med namnet på din fil
    sheet = client.open("FOTMOB data").worksheet("tabell")
    sheet.clear()
    sheet.update(range_name='A1', values=rows)

if __name__ == "__main__":
    main()
