from collections import defaultdict
import pandas as pd
from .api import get_team_chips
from .league import get_league_teams

# Order of chips
CHIP_ORDER = ["wildcard", "freehit", "bboost", "3xc"]  # 3xc = triple captain

def build_chips_table(league_id):
    teams = get_league_teams(league_id)
    rows = []

    for team in teams:
        raw_chips = get_team_chips(team["id"])
        raw_chips = sorted(raw_chips, key=lambda x: x["event"])

        # Track chip usage counts
        chip_count = defaultdict(int)
        chip_dict = {}

        # Fill in used chips
        for chip in raw_chips:
            name = chip["name"]
            chip_count[name] += 1
            col_name = f"{name.title().replace('3Xc','TC')} {chip_count[name]}"  # "Wildcard 1", "FH 1", "BB 1", "TC 1"
            chip_dict[col_name] = f"GW{chip['event']}"

        # Fill unused chips as "Available"
        for c in CHIP_ORDER:
            for i in range(1, 3):
                col_name = f"{c.title().replace('3Xc','TC')} {i}"
                if col_name not in chip_dict:
                    chip_dict[col_name] = "Available"

        chip_dict["Team"] = team["team"]
        chip_dict["Manager"] = team["manager"]
        rows.append(chip_dict)

    df = pd.DataFrame(rows)

    # Sort by most chips remaining
    def chips_remaining(row):
        return sum(1 for col in df.columns if str(row[col]) == "Available")

    df["chips_remaining"] = df.apply(chips_remaining, axis=1)
    df = df.sort_values("chips_remaining", ascending=False).drop(columns=["chips_remaining"])

    # Column order: Team, Manager, then chips in order WC1, FH1, BB1, TC1, WC2, FH2, BB2, TC2
    column_order = ["Team", "Manager"] + [f"{c.title().replace('3Xc','TC')} {i}" for i in range(1,3) for c in CHIP_ORDER]
    df = df[column_order]

    return df

# Optional: helper for Streamlit highlighting
def style_chips(df):

    chip_columns = [col for col in df.columns if col not in ("Team", "Manager")]

    def highlight_chip(val):
        if val != "Available":
            return "background-color: #dc143c"  # crimson
        return ""
    return df.style.applymap(lambda val: "", subset=["Team","Manager"])\
                   .applymap(highlight_chip, subset=chip_columns)
