from get_all_nba_teams import get_all_nba_teams
from get_team_roster import get_team_roster
import pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import CommonTeamRoster
from nba_api.stats.static import teams
import warnings
import re
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def print_all_team_rosters(season=None):
    """
    Retrieves and prints the rosters of all NBA teams for a specified season.
    
    Args:
        season (str, optional): The NBA season in the format "YYYY-YY" (e.g., "2023-24"). 
                                If not provided, defaults to the latest season.
    
    Returns:
        None
    """
    try:
        # Step 1: Retrieve all NBA teams
        all_teams_df = get_all_nba_teams()
        
        if all_teams_df.empty:
            logging.error("No team data available to retrieve rosters.")
            return
        
        # Step 2: Iterate over each team and fetch roster
        for index, team in all_teams_df.iterrows():
            team_name = team['FullName']
            team_abbreviation = team['Abbreviation']
            
            logging.info(f"Processing roster for {team_name} ({team_abbreviation})")
            
            # Fetch the roster for the team
            roster_df = get_team_roster(team_abbreviation, season)
            
            if not roster_df.empty:
                print(f"\n=== {team_name} Roster ({season or 'Latest Season'}) ===")
                print(roster_df.to_string(index=False))
            else:
                print(f"\n=== {team_name} Roster ({season or 'Latest Season'}) ===")
                print("No roster data found.")
        
        logging.info("Completed fetching all team rosters.")
    
    except Exception as e:
        logging.error(f"An error occurred while printing all team rosters: {e}")
