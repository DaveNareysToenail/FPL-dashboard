import streamlit as st
from fpl.league import get_league_teams, build_dataframe 
from fpl.api import get_league_name
from fpl.chips import build_chips_table, style_chips
import pandas as pd
from visualisations.race import race_animate
import tempfile
import os

# Max league size for sim functionality
MAX_LEAGUE_SIZE = 49

# --- Helper function to get league name ---
def fetch_league_name(league_id):
    try:
        # Assume you have a function that fetches league JSON
        # For example, hitting: https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/
        league_name = get_league_name(league_id)  # returns string
        return league_name
    except Exception:
        return "FPL League"  # fallback

# --- 1. League ID input ---
default_league_id = 542576
league_id_input = st.text_input("Enter your League ID:", str(default_league_id))

if league_id_input:
    try:
        league_id = int(league_id_input)

        # Fetch league name dynamically
        league_name = fetch_league_name(league_id)

        # --- 2. Set dynamic page title & header ---
        st.set_page_config(page_title=f"{league_name} Dashboard", layout="wide")
        st.title(f"{league_name} Dashboard ⚽")

        # --- 3. Fetch teams for dropdown ---
        try:
            teams = get_league_teams(league_id)
            team_options = {f"{t['team']} ({t['manager']})": t['id'] for t in teams}

            selected_team_name = st.selectbox(
                "Select your team:",
                options=list(team_options.keys())
            )
            team_id = team_options[selected_team_name]

            # --- 4. Show league table ---
            st.subheader("Current League Table")
            df = build_dataframe(league_id)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # --- 4.25. Show league-wide chip usage ---
            st.subheader("Chips Usage - League Overview")
            df_chips = build_chips_table(league_id)
            styled_chips = style_chips(df_chips)
            st.dataframe(styled_chips, use_container_width=True, hide_index=True)


            #4.5 - week-by-week anim

            st.subheader("League Race Animation")
            if st.button("Show League Race Chart"):
                with st.spinner("Generating animation... This may take a few seconds..."):
                    try:
                        # Temporary MP4 file
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                        temp_path = temp_file.name
                        temp_file.close()  # close so Matplotlib can write

                        # Generate MP4
                        race_animate(league_id, user_team_id=team_id, output_path=temp_path)

                        # Display video in Streamlit
                        st.video(temp_path)

                        # Clean up temp file
                        os.unlink(temp_path)

                    except Exception as e:
                        st.error(f"Failed to generate race animation: {e}")

            # -- 4.9. Check league size for simulation ---
            if len(teams) > MAX_LEAGUE_SIZE:
                st.warning(
                    f"This league has more than {len(teams)} teams."
                    f"Simulations are limited to teams with {MAX_LEAGUE_SIZE} teams or fewer."
                )
                st.stop()

            # --- 5. Monte Carlo simulation button ---
            from fpl.monte_carlo import run_simulation

            st.subheader("Season Sim")

            if st.button("Simulate rest of season: "):
                with st.spinner("Loading..."):
                    st.subheader("Season Projection after 10,000 simulations")
                    sim_results = run_simulation(league_id, team_id)
                st.subheader("Simulation Results")
                st.metric("Expected Final Rank", sim_results["expected_rank"])
                st.metric("Win Probability", f"{sim_results['win_probability']:.1%}")

                projected_table = sim_results["projected_table"]

                def highlight_team(row):
                    if row["rank"] == sim_results["expected_rank"]:
                        return ["background-color: #326c56"] * len(row)
                    return [""] * len(row)
                
                df_proj = pd.DataFrame(projected_table)

                st.subheader("Projected League Table")
                styled =(
                    df_proj.style
                    .format({"projected_points": "{:.0f}"})
                    .apply(highlight_team, axis=1)
                    )

                st.dataframe(styled, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error fetching teams or table: {e}")

    except ValueError:
        st.error("League ID must be a number")
