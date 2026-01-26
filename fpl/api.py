import requests

BASE_URL = "https://fantasy.premierleague.com/api"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://fantasy.premierleague.com/"
}

def get_league_standings(league_id): 
    url = f"{BASE_URL}/leagues-classic/{league_id}/standings"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_league_name(league_id):
    data = get_league_standings(league_id)
    return data["league"]["name"]

def get_team_history(entry_id):
    url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    return [gw["points"] for gw in data.get("current", [])]




