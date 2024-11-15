import pandas as pd
from nba_api.stats.static import teams
import warnings

import functools

@functools.lru_cache(maxsize=1)
def get_all_nba_teams_cached():
    return get_all_nba_teams()


def get_all_nba_teams():
    """
    Retrieves all NBA teams with detailed information using the nba_api.
    
    Returns:
        pd.DataFrame: DataFrame containing TeamID, FullName, Abbreviation, Nickname, City, State, YearFounded.
    """
    try:
        # Suppress warnings from nba_api
        warnings.filterwarnings("ignore")
        
        # Step 1: Retrieve all NBA teams
        nba_teams = teams.get_teams()
        
        if not nba_teams:
            print("No team data found.")
            return pd.DataFrame(columns=['TeamID', 'FullName', 'Abbreviation', 'Nickname', 'City', 'State', 'YearFounded'])
        
        # Step 2: Create a DataFrame from the team data
        teams_df = pd.DataFrame(nba_teams)
        
        # Step 3: Check if required columns are present
        required_columns = ['id', 'full_name', 'abbreviation', 'nickname', 'city', 'state', 'year_founded']
        missing_columns = [col for col in required_columns if col not in teams_df.columns]
        
        if missing_columns:
            print(f"Missing columns in team data: {missing_columns}")
            return pd.DataFrame(columns=['TeamID', 'FullName', 'Abbreviation', 'Nickname', 'City', 'State', 'YearFounded'])
        
        # Step 4: Rename columns for clarity
        teams_df = teams_df.rename(columns={
            'id': 'TeamID',
            'full_name': 'FullName',
            'abbreviation': 'Abbreviation',
            'nickname': 'Nickname',
            'city': 'City',
            'state': 'State',
            'year_founded': 'YearFounded'
        })
        
        # Step 5: Select and order the desired columns
        teams_df = teams_df[['TeamID', 'FullName', 'Abbreviation', 'Nickname', 'City', 'State', 'YearFounded']]
        
        return teams_df.reset_index(drop=True)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(columns=['TeamID', 'FullName', 'Abbreviation', 'Nickname', 'City', 'State', 'YearFounded'])
