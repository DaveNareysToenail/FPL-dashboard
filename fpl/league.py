import pandas as pd
from .api import get_league_standings 

def get_league_teams(league_id): #function to return teams

    data = get_league_standings(league_id) #calls api from inside fpl.api
    teams = [] #empty list to hold dicts of id, team name & manager
    
    for t in data["standings"]["results"]: #iterate over all items in results
        teams.append({
            "id": t["entry"], #Team ID
            "team": t["entry_name"], #Team name
            "manager": t["player_name"] #Manager name
        })

    return teams   

def build_dataframe(league_id): #function to build dataframe i.e. league table

    data = get_league_standings(league_id) #call get league standings to get the data from API
    rows = [] #initialize empty list for rows

    for t in data["standings"]["results"]:
        rows.append({
            "rank": t["rank"], #League Position
            "team": t["entry_name"], #Team Name
            "manager": t["player_name"], #Manager
            "total_points": t["total"], #Total Points
            "team_id": t["entry"] #Team ID - will hide in visualisation but could be handy to have available
        })

    df = pd.DataFrame(rows) #Setup dataframe

    df = df.sort_values("rank").reset_index(drop=True) #Explicitly sort by rank for safety

    return df










