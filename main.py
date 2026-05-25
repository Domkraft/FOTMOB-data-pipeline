import os
import json
import gspread
from fotmob_api import Fotmob
from google.oauth2.service_account import Credentials

def main():
    # Autentisering till Google (samma som förut)
    creds_dict = json.loads(os.environ['GCP_CREDENTIALS'])
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    # Använd fotmob-api biblioteket
    fm = Fotmob()
    
    # Hämta ligatabell för Allsvenskan (ID 67)
    # Biblioteket sköter headers och anropsstruktur åt dig
    league_data = fm.get_league(league_id="67")
    
    # Tabellen brukar ligga under 'table' i svaret
    table_data = league_data['table'][0]['data']['table']['all']
    
    # Förbered rader
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
    
    # Uppdatera Google Sheet
    sheet = client.open("FOTMOB data").worksheet("tabell")
    sheet.clear()
    sheet.update(range_name='A1', values=rows)
    print("Tabellen har uppdaterats via biblioteket!")

if __name__ == "__main__":
    main()
