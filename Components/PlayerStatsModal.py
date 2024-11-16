from textual.screen import ModalScreen
from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button, DataTable, Label
from textual.containers import Container, Horizontal, VerticalScroll
from nba_api_functions.player_profile import get_last_n_games_playergamelog
from nba_api.stats.static import players

class PlayerStatsModal(ModalScreen):
    """Modal screen for displaying player statistics."""
    
    def __init__(self, player_id: str):
        super().__init__()
        self.player_id = player_id
        self.player_name = "Unknown Player"
        try:
            # Get player info from NBA API
            player_info = players.find_player_by_id(int(player_id))
            if player_info:
                self.player_name = player_info['full_name']
        except Exception as e:
            print(f"Error fetching player name: {e}")
        
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label(f"{self.player_name} - Statistics", id="dialog-title")
            yield DataTable(id="stats-table")
            yield Button("Close", variant="primary", id="close-button")
            
    def on_mount(self):
        stats_df = get_last_n_games_playergamelog(int(self.player_id))
        if stats_df is not None:
            table = self.query_one("#stats-table", DataTable)
            for column in stats_df.columns:
                table.add_column(str(column))
            for _, row in stats_df.iterrows():
                table.add_row(*[str(val) for val in row])
                
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close-button":
            self.dismiss()