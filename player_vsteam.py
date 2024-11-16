from nba_api.stats.endpoints import PlayerGameLogs
from nba_api.stats.static import players, teams

def get_player_id(player_name):
    player = next((player for player in players.get_players() if player_name.lower() in player['full_name'].lower()), None)
    print(f"Player ID for {player_name}: {player['id'] if player else 'Not Found'}")
    return player['id'] if player else None

def get_team_abbreviation(team_name):
    team = next((team for team in teams.get_teams() if team_name.lower() in team['full_name'].lower()), None)
    print(f"Team Abbreviation for {team_name}: {team['abbreviation'] if team else 'Not Found'}")
    return team['abbreviation'] if team else None

def get_player_stats_vs_team(player_name, team_name, current_season="2024-25"):
    player_id = get_player_id(player_name)
    team_abbr = get_team_abbreviation(team_name)

    if not player_id or not team_abbr:
        return f"Could not find IDs for {'player' if not player_id else 'team'}."

    # Fetch current season game logs
    print(f"Fetching game logs for {current_season}...")
    game_logs_current = PlayerGameLogs(season_nullable=current_season, player_id_nullable=player_id).get_normalized_dict()
    games_current = [game for game in game_logs_current['PlayerGameLogs'] if team_abbr in game['MATCHUP']]

    print(f"Games Found in Current Season: {len(games_current)}")

    # Check if we need last season's games
    if len(games_current) < 5:
        start_year = int(current_season[:4]) - 1
        end_year = start_year + 1
        last_season = f"{start_year}-{str(end_year)[-2:]}"
        print(f"Fetching game logs for {last_season}...")
        try:
            game_logs_last = PlayerGameLogs(season_nullable=last_season, player_id_nullable=player_id).get_normalized_dict()
            games_last = [game for game in game_logs_last['PlayerGameLogs'] if team_abbr in game['MATCHUP']]
            games_current.extend(games_last)
            print(f"Games Found in Last Season: {len(games_last)}")
        except Exception as e:
            print(f"Error fetching last season's game logs: {e}")

    # Limit to the last 5 games
    last_five_games = games_current[:5]

    if not last_five_games:
        return f"No games found for {player_name} against {team_name} in the past two seasons."

    formatted_output = f"Player: {player_name}\nTeam: {team_name}\nGames Played: {len(last_five_games)}\n\n"
    for game in last_five_games:
        formatted_output += (
            f"  Game ID: {game['GAME_ID']}, Date: {game['GAME_DATE']}, "
            f"Points: {game['PTS']}, Rebounds: {game['REB']}, Assists: {game['AST']}\n"
        )
    return formatted_output

# Example usage
if __name__ == "__main__":
    player_name = "De'Aaron Fox"
    team_name = "Minnesota Timberwolves"
    stats = get_player_stats_vs_team(player_name, team_name)
    print(stats)
