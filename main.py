import os
import json
import gspread
import soccerdata as sd
from google.oauth2.service_account import Credentials

def main():
    # 1. Autentisering för Google Sheets
    creds_raw = os.environ.get('GCP_CREDENTIALS')
    if not creds_raw:
        raise ValueError("GCP_CREDENTIALS secret not found!")
    
    creds_dict = json.loads(creds_raw)
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open("FOTMOB data")
    
    # 2. Hämta data via soccerdata (FBRef är källan)
    # 'SWE-Allsvenskan' är ligakoden för Allsvenskan
    fbref = sd.FBref(leagues='SWE-Allsvenskan', seasons='26')
    
    # --- UPPDATERA TABELL ---
    table = fbref.read_league_table()
    # Återställ index för att få 'Lag' som en kolumn
    table = table.reset_index()
    
    # Förbered rader för tabellen (inklusive PPM-beräkning)
    rows_table = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng", "PPM"]]
    
    for _, row in table.iterrows():
        played = row['MP']
        pts = row['Pts']
        ppm = round(pts / played, 2) if played > 0 else 0
        
        rows_table.append([
            row['Rk'], row['Squad'], played, row['W'], row['D'], row['L'],
            row['GF'], row['GA'], row['GD'], pts, ppm
        ])
    
    sheet_table = spreadsheet.worksheet("tabell")
    sheet_table.clear()
    sheet_table.update(range_name='A1', values=rows_table)
    
    # --- UPPDATERA MATCHER ---
    schedule = fbref.read_schedule()
    schedule = schedule.reset_index()
    
    rows_matches = [["Datum/Tid", "Omgång", "Hemmalag", "Bortalag", "Hemmalagsmål", "Bortalagsmål"]]
    
    for _, row in schedule.iterrows():
        # Hantera fall där mål saknas (kommande matcher)
        home_score = row['Home Score'] if not row['Home Score'] is None else 0
        away_score = row['Away Score'] if not row['Away Score'] is None else 0
        
        rows_matches.append([
            str(row['Date']),
            row['Round'],
            row['Home'],
            row['Away'],
            int(home_score),
            int(away_score)
        ])
    
    sheet_matches = spreadsheet.worksheet("matcher")
    sheet_matches.clear()
    sheet_matches.update(range_name='A1', values=rows_matches)
    
    print("Tabell och matcher har uppdaterats via soccerdata!")

if __name__ == "__main__":
    main()
