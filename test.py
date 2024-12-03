from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input


class Name(Widget):
    who = reactive("name")

    def __init__(self):
        super().__init__()

    def render(self) -> str:
        return f"Hello, {self.who}!"


class WatchApp(App):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter your name")
        yield Name()

    @on(Input.Changed)
    def update_who(self, event: Input.Changed) -> None:
        self.query_one(Name).who = event.input.value


if __name__ == "__main__":
    WatchApp().run()
