import numpy as np
from collections import defaultdict

from .api import get_team_history
from .league import get_league_teams


# Monte Carlo simulation to estimate projected rank and win probability
# Assumes GW points ~ Normal(mean, std)
# Applies floors to avoid degenerate distributions


def run_simulation(league_id, team_id, n_sims=10_000):
 
    teams = get_league_teams(league_id)

    TOTAL_GWS = 38
    STD_FLOOR = 5.0

    team_data = {}

    # --- Build empirical distributions from real data ---
    for team in teams:
        entry_id = team["id"]

        gw_points = get_team_history(entry_id)

        team_data[entry_id] = {
            "name": team["team"],
            "manager": team["manager"],
            "current_points": sum(gw_points),
            "mean": np.mean(gw_points),
            "std": max(np.std(gw_points), STD_FLOOR),
            "played_gws": len(gw_points),
        }

    # Assume all teams have played same number of GWs
    played_gws = max(t["played_gws"] for t in team_data.values())
    remaining_gws = TOTAL_GWS - played_gws

    final_points = defaultdict(list)

    # --- Monte Carlo simulations ---
    for _ in range(n_sims):
        for entry_id, team in team_data.items():

            simulated = np.random.normal(
                loc=team["mean"],
                scale=team["std"],
                size=remaining_gws
            )

            # Clamp to plausible FPL bounds
            simulated = np.clip(simulated, 35, 100)

            total = team["current_points"] + simulated.sum()
            final_points[entry_id].append(total)

    # --- Post-processing ---
    mean_final_points = {
        entry_id: np.mean(points)
        for entry_id, points in final_points.items()
    }

    sorted_teams = sorted(
        mean_final_points.items(),
        key=lambda x: x[1],
        reverse=True
    )

    ranks = {
        entry_id: rank + 1
        for rank, (entry_id, _) in enumerate(sorted_teams)
    }

    # --- Win probability ---
    wins = 0
    for i in range(n_sims):
        sim_points = {
            entry_id: final_points[entry_id][i]
            for entry_id in final_points
        }

        winner = max(sim_points, key=sim_points.get)

        if winner == team_id:
            wins += 1

    win_probability = wins / n_sims

    return {
        "expected_rank": ranks.get(team_id),
        "win_probability": win_probability,
        "mean_final_points": mean_final_points,
    }
