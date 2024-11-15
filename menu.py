from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Static, Button, DataTable
from nba_api.stats.static import teams
from nba_api_functions.get_todays_nba_games import get_todays_nba_games
from nba_api_functions.get_team_roster import get_team_roster
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CombiningLayoutsExample(App):
    CSS_PATH = "combining_layouts.tcss"
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane"):
                games_df = get_todays_nba_games()
                if not games_df.empty:
                    for _, game in games_df.iterrows():
                        game_text = (
                            f"{game['HomeTeam']} vs {game['VisitorTeam']}\n"
                            f"Arena: {game['Arena']}\n"
                            f"Time: {game['GameTime']}"
                        )
                        yield Static(game_text)
                else:
                    yield Static("No games scheduled today")
            with Horizontal(id="top-right"):
                with VerticalScroll():
                    nba_teams = teams.get_teams()
                    for team in nba_teams:
                        valid_id = f"team_{team['id']}"
                        yield Button(f"{team['full_name']}", id=valid_id)
            with Container(id="bottom-right"):
                self.roster_table = DataTable()
                yield self.roster_table

    def update_roster_display(self, roster_df: pd.DataFrame):
        """Update the roster table with team data."""
        logger.info("Updating roster display")
        try:
            self.roster_table.clear()
            
            if not roster_df.empty:
                # Add desired columns as defined in get_team_roster
                desired_columns = [
                    'PLAYER', 'NUM', 'POSITION', 'HEIGHT', 'WEIGHT',
                    'BIRTH_DATE', 'AGE', 'EXP', 'SCHOOL', 'PLAYER_ID'
                ]
                
                # Add columns to table
                for column in desired_columns:
                    if column in roster_df.columns:
                        self.roster_table.add_column(column)
                
                # Add rows
                for _, row in roster_df.iterrows():
                    self.roster_table.add_row(*[row[col] for col in desired_columns if col in roster_df.columns])
                logger.info(f"Added {len(roster_df)} rows to roster table")
            else:
                logger.warning("Received empty roster DataFrame")
        except Exception as e:
            logger.error(f"Error updating roster display: {str(e)}")

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

if __name__ == "__main__":
    logger.info("Starting NBA TUI application...")
    app = CombiningLayoutsExample()
    app.run()