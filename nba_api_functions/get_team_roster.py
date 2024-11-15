import pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import CommonTeamRoster
from nba_api.stats.static import teams
import warnings
import re
import logging
from nba_api_functions.get_all_nba_teams import get_all_nba_teams


def get_team_roster(team, season=None):
    """
    Retrieves the roster of players for a specified NBA team and season.
    
    Args:
        team (str): The name or abbreviation of the NBA team (e.g., "Los Angeles Lakers" or "LAL").
        season (str, optional): The NBA season in the format "YYYY-YY" (e.g., "2023-24"). Defaults to the latest season.
    
    Returns:
        pd.DataFrame: DataFrame containing player details such as PLAYER, NUM, POSITION, HEIGHT, WEIGHT, BIRTH_DATE, AGE, EXP, SCHOOL, PLAYER_ID.
    """
    try:
        # Suppress warnings from nba_api
        warnings.filterwarnings("ignore")
        
        # Step 1: Retrieve all NBA teams
        all_teams_df = get_all_nba_teams()
        
        if all_teams_df.empty:
            logging.error("No team data available to map the team name or abbreviation.")
            return pd.DataFrame()
        
        # Step 2: Normalize team input for matching
        team_input = team.strip().lower()
        
        # Attempt to match by FullName or Abbreviation
        matched_team = all_teams_df[
            (all_teams_df['FullName'].str.lower() == team_input) |
            (all_teams_df['Abbreviation'].str.lower() == team_input)
        ]
        
        if matched_team.empty:
            logging.error(f"Team '{team}' not found. Please check the team name or abbreviation.")
            return pd.DataFrame()
        
        # If multiple matches found, select the first one
        team_info = matched_team.iloc[0]
        team_id = team_info['TeamID']
        team_full_name = team_info['FullName']
        team_abbreviation = team_info['Abbreviation']
        
        logging.info(f"Fetching roster for Team: {team_full_name} (ID: {team_id}, Abbreviation: {team_abbreviation})")
        
        # Step 3: Determine the season if not provided
        if not season:
            today = date.today()
            year = today.year
            month = today.month
            # NBA season typically starts in October
            if month >= 10:
                season_start_year = year
            else:
                season_start_year = year - 1
            season = f"{season_start_year}-{str(season_start_year + 1)[-2:]}"
            logging.info(f"No season provided. Defaulting to the latest season: {season}")
        else:
            # Validate season format
            if not re.match(r'^\d{4}-\d{2}$', season):
                logging.error("Invalid season format. Please use 'YYYY-YY' (e.g., '2023-24').")
                return pd.DataFrame()
        
        # Step 4: Fetch the team roster using CommonTeamRoster
        roster = CommonTeamRoster(
            team_id=team_id,
            season=season,
            timeout=10
        )
        
        # Step 5: Extract the roster data
        roster_df = roster.common_team_roster.get_data_frame()
        
        if roster_df.empty:
            logging.info(f"No roster data found for Team '{team_full_name}' in Season '{season}'.")
            return pd.DataFrame()
        
        # Step 6: Clean and format the roster DataFrame
        # Rename columns for clarity if needed
        # (Assuming columns are already appropriately named)
        
        # Optionally, select specific columns
        desired_columns = [
            'PLAYER', 'NUM', 'POSITION', 'HEIGHT', 'WEIGHT',
            'BIRTH_DATE', 'AGE', 'EXP', 'SCHOOL', 'PLAYER_ID'
        ]
        
        # Check if all desired columns are present
        missing_cols = [col for col in desired_columns if col not in roster_df.columns]
        if missing_cols:
            logging.warning(f"Missing columns in roster data: {missing_cols}")
            # Proceed with available columns
            desired_columns = [col for col in desired_columns if col in roster_df.columns]
        
        roster_df = roster_df[desired_columns]
        
        # Reset index for cleanliness
        roster_df.reset_index(drop=True, inplace=True)
        
        logging.info(f"Retrieved roster for Team '{team_full_name}' in Season '{season}'.")
        
        return roster_df
    
    except Exception as e:
        logging.error(f"An error occurred while fetching the team roster: {e}")
        return pd.DataFrame()
