import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import pandas as pd
import tempfile
import os
from fpl.api import get_league_name, get_team_history
from fpl.league import get_league_teams

# --- Config ---
FPS = 1          # Animation speed (frames per second)
BAR_COUNT = None  # None = show all teams; set to int for top N


def race_animate(league_id, user_team_id=None, output_path="race.mp4"):
    """
    Generate a racing bar chart for an FPL league and save as MP4.

    :param league_id: int, FPL league ID
    :param user_team_id: int, highlight this team
    :param output_path: str, file path to save MP4
    :return: path to saved MP4 video
    """
    # --- Fetch league info ---
    teams = get_league_teams(league_id)
    league_name = get_league_name(league_id)

    # --- Build cumulative points dataframe ---
    rows = []
    for team in teams:
        team_id = team["id"]
        gw_points = get_team_history(team_id)

        if not gw_points:
            continue

        total = 0
        for gw, pts in enumerate(gw_points, start=1):
            total += pts
            rows.append({
                "GW": gw,
                "Team": team["team"],
                "Manager": team["manager"],
                "Points": total,
                "ID": team_id
            })

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No gameweek data found for any team in this league.")

    frames = sorted(df["GW"].unique())

    # --- Setup figure ---
    fig, ax = plt.subplots(figsize=(12, 7))

    def draw_bars(gw):
        ax.clear()
        data = df[df["GW"] == gw].sort_values("Points", ascending=True).reset_index(drop=True)

        if BAR_COUNT:
            data = data.tail(BAR_COUNT)

        # Highlight user team
        colors = ["#326c56" if (user_team_id is not None and tid == user_team_id) else "#4e79a7"
                  for tid in data["ID"]]

        ax.barh(data["Team"], data["Points"], color=colors)

        # Annotate points
        for i, points in enumerate(data["Points"].values):
            ax.text(points + 1, i, f"{int(points)}", va="center", fontsize=9)

        ax.set_title(f"{league_name} League Standings - Gameweek {gw}", fontsize=16)
        ax.set_xlabel("Total Points")
        ax.set_xlim(0, df["Points"].max() * 1.05)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

    ani = FuncAnimation(fig, lambda frame: draw_bars(frame), frames=frames, interval=1000 // FPS)

    # --- Save animation to MP4 file ---
    writer = FFMpegWriter(fps=FPS)
    ani.save(output_path, writer=writer)
    plt.close(fig)
    return output_path
