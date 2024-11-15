import pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import teams
import warnings
import re

def get_yesterdays_nba_games():
    """
    Fetches yesterday's NBA games using the nba_api and returns a pandas DataFrame containing
    the game date, arena name, home team, visitor team, and scheduled game time.
    
    Returns:
        pd.DataFrame: DataFrame with columns ['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime']
    """
    try:
        # Suppress warnings from nba_api
        warnings.filterwarnings("ignore")
        
        # Step 1: Calculate yesterday's date using the date class
        yesterday = date.today() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%m/%d/%Y')  # Format: MM/DD/YYYY
        
        # Step 2: Fetch the scoreboard data for yesterday using ScoreboardV2
        sb = scoreboardv2.ScoreboardV2(game_date=yesterday_str, timeout=10)
        
        # Step 3: Extract the game header data as a DataFrame
        game_header_df = sb.game_header.get_data_frame()
        
        if game_header_df.empty:
            print("No game data found for yesterday. Please verify the date and try again.")
            return pd.DataFrame(columns=['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime'])
        
        # Step 4: Retrieve team information and map team IDs to team names
        all_teams = teams.get_teams()
        team_id_to_name = {team['id']: team['full_name'] for team in all_teams}
        game_header_df['HomeTeam'] = game_header_df['HOME_TEAM_ID'].map(team_id_to_name)
        game_header_df['VisitorTeam'] = game_header_df['VISITOR_TEAM_ID'].map(team_id_to_name)
        
        # Step 5: Parse GAME_DATE_EST to datetime and extract date
        game_header_df['GameDate'] = pd.to_datetime(game_header_df['GAME_DATE_EST']).dt.date
        
        # Step 6: Extract Arena Name
        game_header_df['Arena'] = game_header_df['ARENA_NAME']
    
        
        game_header_df['GameTime'] = game_header_df['GAME_STATUS_TEXT']
        
        # Step 8: Select the relevant columns
        result_df = game_header_df[['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime']].copy()
        
        return result_df.reset_index(drop=True)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(columns=['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime'])

if __name__ == "__main__":
    yesterdays_games = get_yesterdays_nba_games()
    if not yesterdays_games.empty:
        print("Yesterday's NBA Games:")
        print(yesterdays_games)
    else:
        print("No games found for yesterday.")
