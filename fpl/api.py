import requests

BASE_URL = "https://fantasy.premierleague.com/api"

def get_league_standings(league_id): 
    url = f"{BASE_URL}/leagues-classic/{league_id}/standings"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_league_name(league_id):
    data = get_league_standings(league_id)
    return data["league"]["name"]



