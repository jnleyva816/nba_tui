from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Static, Button, DataTable, Label, Input  # Add Input to imports
from textual import events
from nba_api.stats.static import teams, players
from nba_api_functions.get_todays_nba_games import get_todays_nba_games
from nba_api_functions.get_team_roster import get_team_roster
from nba_api_functions.player_profile import get_last_n_games_playergamelog
from generate_urls import get_urls_from_db
import pandas as pd
import logging
import webbrowser
from Components.PlayerStatsModal import PlayerStatsModal
from Components.GameURLModal import GameURLModal
from datetime import datetime


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class nba_tui(App):
    CSS_PATH = "combining_layouts.tcss"
    
    def __init__(self):
        super().__init__()
        self.player_id_map = {}  # Store player ID mapping
        self.game_urls = {}
        self.all_team_buttons = []  # Store all team buttons
        self.current_roster_df = None  # Store current roster for filtering

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Container(id="left-pane"):
                with VerticalScroll(id="left-pane"):
                    games_df = get_todays_nba_games()
                    urls = get_urls_from_db()
                    self.game_urls = {i: url[1] for i, url in enumerate(urls)}
                    
                    if not games_df.empty:
                        for idx, game in games_df.iterrows():
                            # Convert time to readable format
                            try:
                                game_time = datetime.strptime(game['GameTime'], '%Y-%m-%dT%H:%M:%S')
                                formatted_time = game_time.strftime('%I:%M %p')
                            except:
                                formatted_time = game['GameTime']
                                
                            game_text = (
                                f"{game['HomeTeam']} vs {game['VisitorTeam']}\n"
                                f"Arena: {game['Arena']}\n"
                                f"Time: {formatted_time}"
                            )
                            game_button = Button(game_text, id=f"game_{idx}", classes="game-button")
                            yield game_button
                    else:
                        yield Static("No games scheduled today")
            
            # Separate container for teams section
            with Container(id="teams-section"):
                yield Input(placeholder="Search teams...", id="team-search")
                with VerticalScroll(id="teams-list"):
                    try:
                        nba_teams = teams.get_teams()
                        logger.info(f"Fetched {len(nba_teams)} teams")
                        for team in nba_teams:
                            valid_id = f"team_{team['id']}"
                            team_button = Button(f"{team['full_name']}", id=valid_id, classes="team-button")
                            self.all_team_buttons.append(team_button)
                            yield team_button
                    except Exception as e:
                        logger.error(f"Error loading teams: {str(e)}")
                        yield Static("Error loading teams")
            with Container(id="bottom-right"):
                self.roster_table = DataTable()
                self.roster_table.styles.width = "100%"
                self.roster_table.styles.height = "100%"
                yield self.roster_table

    def update_roster_display(self, roster_df: pd.DataFrame):
        """Update the roster table with team data."""
        self.current_roster_df = roster_df  # Store the full roster
        self._filter_and_display_roster()

    def _filter_and_display_roster(self, search_term: str = ""):
        """Filter and display roster based on search term."""
        try:
            self.roster_table.clear()
            if self.current_roster_df is not None and not self.current_roster_df.empty:
                filtered_df = self.current_roster_df
                if search_term:
                    filtered_df = self.current_roster_df[
                        self.current_roster_df['PLAYER'].str.lower().str.contains(search_term.lower())
                    ]

                desired_columns = [
                    'PLAYER', 'NUM', 'POSITION', 'HEIGHT', 'WEIGHT',
                    'BIRTH_DATE', 'AGE', 'EXP', 'SCHOOL'
                ]
                
                for column in desired_columns:
                    if column in filtered_df.columns:
                        self.roster_table.add_column(column)
                
                for _, row in filtered_df.iterrows():
                    row_data = []
                    for col in desired_columns:
                        if col in filtered_df.columns:
                            row_data.append(str(row[col]))
                    self.player_id_map[row['PLAYER']] = row['PLAYER_ID']
                    self.roster_table.add_row(*row_data)

        except Exception as e:
            logger.error(f"Error filtering roster: {str(e)}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        logger.info(f"Button pressed: {event.button.id}")
        if event.button.id and event.button.id.startswith("team_"):
            try:
                team_name = str(event.button.label)
                logger.info(f"Fetching roster for {team_name}")
                roster_df = get_team_roster(team_name)
                self.update_roster_display(roster_df)
            except Exception as e:
                logger.error(f"Error handling button press: {str(e)}")
        button_name = event.button.name
        if button_name and button_name.startswith("player_"):
            player_id = button_name.split("_")[1]
            await self.handle_player_click(player_id)
        if event.button.id and event.button.id.startswith("game_"):
            game_idx = int(event.button.id.split("_")[1])
            if game_idx in self.game_urls:
                game_url = self.game_urls[game_idx]
                modal = GameURLModal(game_url)
                await self.push_screen(modal)

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected):
        """Handle cell selection in the roster table."""
        try:
            # First column (index 0) contains player names
            if event.coordinate.column == 0:  
                player_name = event.value
                if player_name in self.player_id_map:
                    player_id = self.player_id_map[player_name]
                    await self.handle_player_click(player_id)
        except Exception as e:
            logger.error(f"Error handling cell selection: {str(e)}")
            logger.error(f"Event details: coordinate={event.coordinate}, value={event.value}")

    async def handle_player_click(self, player_id: str):
        """Handle the player button click event."""
        logger.info(f"Player with ID {player_id} clicked")
        # Show player stats modal
        stats_modal = PlayerStatsModal(player_id)
        await self.push_screen(stats_modal)

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "team-search":
            search_term = event.value.lower()
            logger.info(f"Searching for: {search_term}")
            for button in self.all_team_buttons:
                if search_term in str(button.label).lower():
                    button.styles.display = "block"
                else:
                    button.styles.display = "none"
        elif event.input.id == "player-search":
            self._filter_and_display_roster(event.value)


if __name__ == "__main__":
    logger.info("Starting NBA TUI application...")
    app = nba_tui()
    app.run()
