import pandas as pd
from nba_api.stats.static import teams
import warnings

def inspect_nba_api_teams_columns():
    """
    Retrieves NBA teams data using nba_api.stats.static.teams and inspects its columns.
    
    The function performs the following:
    1. Fetches all NBA teams.
    2. Converts the team data into a pandas DataFrame.
    3. Displays the list of columns.
    4. Shows data types for each column.
    5. Provides a sample of the data.
    
    Returns:
        None
    """
    try:
        # Suppress warnings from nba_api
        warnings.filterwarnings("ignore")
        
        # Step 1: Retrieve all NBA teams
        nba_teams = teams.get_teams()
        
        if not nba_teams:
            print("No team data found.")
            return
        
        # Step 2: Create a DataFrame from the team data
        teams_df = pd.DataFrame(nba_teams)
        
        # Step 3: Display the list of columns
        print("=== NBA Teams Data Columns ===\n")
        print(teams_df.columns.tolist())
        
        # Step 4: Show data types for each column
        print("\n=== Data Types of Each Column ===\n")
        print(teams_df.dtypes)
        
        # Step 5: Provide a sample of the data
        print("\n=== Sample NBA Teams Data ===\n")
        print(teams_df)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    inspect_nba_api_teams_columns()
