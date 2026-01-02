"""
Header widget with tactical ASCII art branding.
"""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive


LOGO_SMALL = """[bold #e0e0e0]PORTWATCH[/]  [dim #666666]v0.1.0[/]"""


class PortWatchHeader(Static):
    """Tactical header with live status."""
    
    port_count: reactive[int] = reactive(0)
    refresh_rate: reactive[float] = reactive(2.0)
    is_scanning: reactive[bool] = reactive(False)
    
    def __init__(self, compact: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.compact = compact
    
    def compose(self) -> ComposeResult:
        yield Static(id="logo")
        yield Static(id="status-bar")
    
    def on_mount(self) -> None:
        self._update_display()
    
    def watch_port_count(self, count: int) -> None:
        self._update_display()
    
    def watch_is_scanning(self, scanning: bool) -> None:
        self._update_display()
    
    def _update_display(self) -> None:
        logo_widget = self.query_one("#logo", Static)
        status_widget = self.query_one("#status-bar", Static)
        
        # Use compact logo if terminal is narrow
        logo_widget.update(LOGO_SMALL if self.compact else LOGO_SMALL)
        
        # Status indicators - minimal style
        scan_indicator = "[#f5a623]● scanning[/]" if self.is_scanning else "[#6c8ebf]● live[/]"
        refresh_text = f"[dim #666666]{self.refresh_rate}s[/]"
        port_text = f"[#e0e0e0]{self.port_count}[/] [dim #666666]ports[/]"

        status_widget.update(
            f"{scan_indicator}  {refresh_text}  {port_text}"
        )
