import sqlite3
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2


DB_NAME = "url_generator.db"


def initialize_database():
    """
    Initializes the SQLite database with the necessary tables.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create tables if they don't already exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_match_id INTEGER NOT NULL,
        last_generated_date TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        generated_date TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def get_last_state():
    """
    Retrieves the last match_id and the date it was generated from the database.
    
    Returns:
        tuple: (last_match_id, last_generated_date)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT last_match_id, last_generated_date FROM state ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)


def update_last_state(last_match_id, generated_date):
    """
    Updates the last match_id and the generation date in the database.
    
    Parameters:
        last_match_id (int): The last match ID generated.
        generated_date (str): The date when URLs were last generated.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO state (last_match_id, last_generated_date) VALUES (?, ?)", (last_match_id, generated_date))
    conn.commit()
    conn.close()


def save_urls_to_db(urls, generated_date):
    """
    Saves the generated URLs to the database.
    
    Parameters:
        urls (list): List of generated URLs.
        generated_date (str): The date when the URLs were generated.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO urls (match_id, url, generated_date) VALUES (?, ?, ?)",
                       [(int(url.split('/')[-1]), url, generated_date) for url in urls])
    conn.commit()
    conn.close()


def get_todays_nba_game_count():
    """
    Fetches today's NBA games using the nba_api and returns the count of games.

    Returns:
        int: The number of NBA games scheduled for today.
    """
    try:
        # Get today's date in MM/DD/YYYY format as required by the API
        today = datetime.today().strftime('%m/%d/%Y')
        
        # Fetch the scoreboard data for today using ScoreboardV2
        sb = scoreboardv2.ScoreboardV2(game_date=today, timeout=10)
        
        # Extract the game header data as a DataFrame
        game_header_df = sb.game_header.get_data_frame()
        
        # Return the count of games
        return len(game_header_df)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0  # Return 0 if there's an error or no games are scheduled


def generate_urls(start_id, n):
    """
    Generates a list of URLs with incremented match IDs.
    
    Parameters:
        start_id (int): The starting match ID.
        n (int): The number of URLs to generate.
    
    Returns:
        list: A list of generated URLs.
    """
    base_url = "https://v2.nba-streams.live/match/"
    urls = [f"{base_url}{match_id}" for match_id in range(start_id + 1, start_id + n + 1)]
    return urls

import sqlite3

def get_urls_from_db():
    """
    Fetches all URLs from the database.

    Returns:
        list: A list of tuples containing (match_id, url, generated_date).
    """
    try:
        conn = sqlite3.connect("url_generator.db")
        cursor = conn.cursor()
        
        # Query to fetch all URLs from the database
        cursor.execute("SELECT match_id, url, generated_date FROM urls ORDER BY id ASC")
        urls = cursor.fetchall()
        
        conn.close()
        return urls

    except sqlite3.Error as e:
        print(f"An error occurred while fetching URLs from the database: {e}")
        return []



def main():
    # Initialize the database and ensure tables exist
    initialize_database()
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if URLs have already been generated for today
    last_match_id, last_generated_date = get_last_state()
    if last_generated_date == today:
        print(f"URLs have already been generated for today ({today}).")
        return

    # Fetch the count of today's NBA games
    game_count = get_todays_nba_game_count()

    if game_count == 0:
        print("No NBA games scheduled for today. Exiting.")
        return

    # Default starting match ID if no state exists
    starting_match_id = last_match_id if last_match_id is not None else 401703377

    # Generate the URLs based on the game count
    urls = generate_urls(starting_match_id, game_count)

    # Save the URLs to the database
    save_urls_to_db(urls, today)

    # Update the last state in the database
    new_last_match_id = starting_match_id + game_count
    update_last_state(new_last_match_id, today)

    # Display the generated URLs
    print(f"\nGenerated {len(urls)} URLs for today's games:")
    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
