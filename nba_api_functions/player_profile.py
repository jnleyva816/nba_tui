from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time
from datetime import datetime

def get_current_season():
    """
    Determines the current NBA season based on the current date.

    Returns:
        str: Season in 'YYYY-YY' format (e.g., '2023-24').
    """
    today = datetime.today()
    year = today.year
    month = today.month

    # NBA seasons typically start in October and end in June
    if month >= 10:  # October to December
        season_start = year
        season_end = year + 1
    else:  # January to September
        season_start = year - 1
        season_end = year

    return f"{season_start}-{str(season_end)[-2:]}"

def get_last_n_games_playergamelog(player_id, n_games=10, timeout=30, retries=3):
    """
    Fetches the last N games' statistics for a given NBA player using PlayerGameLog.

    Parameters:
        player_id (int): The unique NBA player ID.
        n_games (int): Number of recent games to retrieve. Default is 10.
        timeout (int): Time to wait for the API response in seconds. Default is 30.
        retries (int): Number of retry attempts in case of failure. Default is 3.

    Returns:
        pandas.DataFrame or None: DataFrame containing the player's last N games statistics.
    """
    season = get_current_season()
    print(f"Using season: {season}")

    for attempt in range(retries):
        try:
            # Initialize the PlayerGameLog endpoint
            gamelog = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star='Regular Season',
                timeout=timeout
            )

            # Retrieve the game log DataFrame
            gamelog_df = gamelog.get_data_frames()[0]

            if not gamelog_df.empty:
                # Print the column names for verification
                print("\nColumns in the Game Log DataFrame:")
                print(gamelog_df.columns.tolist())

                # Optionally, print the first few rows to inspect the data
                print("\nSample Data:")
                print(gamelog_df.head())

                # Define the desired columns
                desired_columns = [
                    'Player_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA',
                    'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',
                    'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS'
                ]

                # Check if all desired columns are present
                missing_columns = [col for col in desired_columns if col not in gamelog_df.columns]
                if missing_columns:
                    print(f"\nWarning: The following desired columns are missing from the DataFrame: {missing_columns}")
                else:
                    # Select only the desired columns
                    gamelog_df = gamelog_df[desired_columns]

                    # Convert GAME_DATE to datetime with specified format to eliminate warning
                    gamelog_df['GAME_DATE'] = pd.to_datetime(gamelog_df['GAME_DATE'], format='%b %d, %Y')

                    # Sort the DataFrame by GAME_DATE descending and select the top n_games
                    gamelog_df = gamelog_df.sort_values(by='GAME_DATE', ascending=False).head(n_games)

                    return gamelog_df
            else:
                print(f"No game log data found for player ID {player_id} in season {season}.")
                return None

        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                print("Retrying...")
                time.sleep(1)  # Wait before retrying
            else:
                print("All attempts failed.")
                return None

def main():
    """
    Main function to test the get_last_n_games_playergamelog function.
    """
    # Specify the player's full name
    player_name = "LeBron James"

    # Find the player by full name
    matching_players = players.find_players_by_full_name(player_name)

    if not matching_players:
        print(f"No player found with the name '{player_name}'. Please check the name and try again.")
        return

    # Assuming the first match is the desired player
    player = matching_players[0]
    player_id = player['id']
    player_full_name = player['full_name']

    print(f"Fetching the last 10 games for {player_full_name} (Player ID: {player_id})...\n")

    # Fetch the last 10 games' statistics using the alternative function
    last_n_games_df = get_last_n_games_playergamelog(player_id, n_games=10)

    if last_n_games_df is not None:
        print(f"\nLast {len(last_n_games_df)} Games Statistics for {player_full_name}:\n")
        print(last_n_games_df)
    else:
        print("Failed to retrieve game statistics.")

if __name__ == "__main__":
    main()
