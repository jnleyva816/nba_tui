import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import teams
import warnings
def get_todays_nba_games():
    """
    Fetches today's NBA games using the nba_api and extracts game date, arena name,
    home team, visitor team, and scheduled game time (if available) from GAME_STATUS_TEXT.
    
    Returns:
        pd.DataFrame: DataFrame with columns ['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime']
    """
    try:
        # Get today's date in MM/DD/YYYY format as required by the API
        today = datetime.today().strftime('%m/%d/%Y')
        
        # Fetch the scoreboard data for today using ScoreboardV2
        sb = scoreboardv2.ScoreboardV2(game_date=today, timeout=10)
        
        # Extract the game header data as a DataFrame
        game_header_df = sb.game_header.get_data_frame()
        
        if game_header_df.empty:
            print("No game data found for today. Please verify the date and try again.")
            return pd.DataFrame(columns=['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime'])
        
        # Retrieve team information
        all_teams = teams.get_teams()
        team_id_to_name = {team['id']: team['full_name'] for team in all_teams}
        
        # Map HOME_TEAM_ID and VISITOR_TEAM_ID to team names
        game_header_df['HomeTeam'] = game_header_df['HOME_TEAM_ID'].map(team_id_to_name)
        game_header_df['VisitorTeam'] = game_header_df['VISITOR_TEAM_ID'].map(team_id_to_name)
        
        # Parse GAME_DATE_EST to datetime and extract date
        game_header_df['GameDate'] = pd.to_datetime(game_header_df['GAME_DATE_EST']).dt.date
        
        # Extract Arena Name
        game_header_df['Arena'] = game_header_df['ARENA_NAME']
        
        # Apply the function to extract GameTime
        game_header_df['GameTime'] = game_header_df['GAME_STATUS_TEXT']
        
        # Select the relevant columns
        result_df = game_header_df[['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime']].copy()
        
        return result_df.reset_index(drop=True)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(columns=['GameDate', 'Arena', 'HomeTeam', 'VisitorTeam', 'GameTime'])
