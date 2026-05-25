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
    
    # Vi använder samma bas-URL, men vi behöver se om xG-datat döljer sig i samma objekt
    url = "https://www.fotmob.com/api/data/leagues?id=67&ccode3=SWE"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.fotmob.com/',
        'Accept': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Hämta tabell-data
    table_data = data['table'][0]['data']['table']['all']
    
    # DEBUG: Vi printar ut hela första lagets objekt för att hitta xG-nycklar
    print(f"DEBUG: Hela lagobjektet: {table_data[0]}")
    
    rows = [["Position", "Lag", "Spelade", "Vinster", "Oavgjorda", "Förluster", "Gjorda mål", "Insläppta mål", "Målskillnad", "Poäng", "xG", "xGA"]]
    
    for team in table_data:
        goals_str = team.get('scoresStr', '0-0')
        goals_list = goals_str.split('-')
        gjorda = goals_list[0] if len(goals_list) > 0 else 0
        inslappta = goals_list[1] if len(goals_list) > 1 else 0
        
        # Vi letar efter nycklar som innehåller 'xG' i lagobjektet
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
            team.get('expectedGoals', 0), # Gissning på nyckelnamn
            team.get('expectedGoalsAgainst', 0) # Gissning på nyckelnamn
        ])
    
    sheet = client.open("FOTMOB data").worksheet("tabell")
    sheet.clear()
    sheet.update(range_name='A1', values=rows)
    print("Tabell uppdaterad. Kolla loggen för DEBUG-info om xG-nycklar!")

if __name__ == "__main__":
    main()
