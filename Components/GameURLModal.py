from textual.screen import ModalScreen
from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button, DataTable, Label
from textual.containers import Container, Horizontal, VerticalScroll
import webbrowser

class GameURLModal(ModalScreen):
    def __init__(self, game_url: str):
        super().__init__()
        self.game_url = game_url
        
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("Game Stream URL", id="dialog-title")
            yield Label(self.game_url, id="url-text")  # Add URL display
            yield Button("Open in Browser", id="url-button", variant="primary")
            yield Button("Close", id="close-button")
            
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "url-button":
            webbrowser.open(self.game_url)
        elif event.button.id == "close-button":
            self.dismiss()
