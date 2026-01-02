"""
PORTWATCH - Main Application

A tactical port scanner dashboard for developers.
"""

import logging

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Static, Header, Input
from textual.binding import Binding
from textual.timer import Timer
from textual import work

from portwatch.scanner import scan_ports, PortInfo
from portwatch.actions import kill_process, open_in_browser, copy_to_clipboard
from portwatch.widgets import PortTable, ActionModal, PortWatchHeader
from portwatch.widgets.action_modal import ConfirmKillModal

# Create logger for this module
logger = logging.getLogger("portwatch.app")


# Minimal Monochrome color scheme CSS
MINIMAL_CSS = """
$primary: #e0e0e0;
$secondary: #6c8ebf;
$accent: #f5a623;
$warning: #f5a623;
$error: #d64545;
$success: #6c8ebf;
$background: #000000;
$surface: #0a0a0a;
$surface-lighten-1: #141414;
$surface-lighten-2: #1e1e1e;
$text: #e0e0e0;
$text-muted: #666666;

Screen {
    background: $background;
}

#main-container {
    height: 100%;
    padding: 0 1;
}

#header-container {
    height: auto;
    padding: 0;
    margin-bottom: 0;
}

#table-container {
    height: 1fr;
    border: solid $surface-lighten-2;
    background: $background;
}

PortTable {
    height: 100%;
    background: $background;
}

PortTable > .datatable--header {
    background: $surface;
    color: $text-muted;
    text-style: bold;
}

PortTable > .datatable--cursor {
    background: $secondary 25%;
}

PortTable > .datatable--hover {
    background: $surface-lighten-1;
}

#status-bar {
    dock: bottom;
    height: 1;
    background: $background;
    color: $text-muted;
    padding: 0 1;
}

#notification {
    dock: bottom;
    height: auto;
    background: $surface-lighten-1;
    color: $text;
    padding: 0 2;
    margin: 0 1 1 1;
    display: none;
}

#notification.visible {
    display: block;
}

#notification.success {
    background: $surface-lighten-1;
    border: solid $secondary;
}

#notification.error {
    background: #1a0a0a;
    border: solid $error;
}

Footer {
    background: $surface;
}

Footer > .footer--key {
    background: $surface-lighten-2;
    color: $text;
}

Footer > .footer--description {
    color: $text-muted;
}

#search-container {
    height: auto;
    padding: 0;
    margin-bottom: 1;
    display: none;
}

#search-container.visible {
    display: block;
}

#search-input {
    background: $surface;
    border: solid $surface-lighten-2;
    color: $text;
    padding: 0 1;
}

#search-input:focus {
    border: solid $secondary;
}

#search-input > .input--placeholder {
    color: $text-muted;
}

#search-input > .input--cursor {
    background: $secondary;
    color: $background;
}
"""


class PortWatchApp(App):
    """
    Tactical Port Scanner Dashboard
    """
    
    CSS = MINIMAL_CSS
    
    TITLE = "PORTWATCH"
    SUB_TITLE = "Tactical Port Scanner"
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "show_actions", "Actions", show=True),
        Binding("b", "open_browser", "Browser"),
        Binding("k", "kill_process", "Kill"),
        Binding("c", "copy_port", "Copy"),
        Binding("slash", "search", "Search"),
        Binding("escape", "clear_search", "Clear", show=False),
        Binding("1", "refresh_rate_1", "1s", show=False),
        Binding("2", "refresh_rate_2", "2s", show=False),
        Binding("5", "refresh_rate_5", "5s", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.ports: list[PortInfo] = []
        self.refresh_rate: float = 2.0
        self.auto_refresh_timer: Timer | None = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="main-container"):
            with Container(id="header-container"):
                yield PortWatchHeader(id="portwatch-header")

            with Container(id="search-container"):
                yield Input(placeholder="Filter ports... (port, process, service, category)", id="search-input")

            with Container(id="table-container"):
                yield PortTable(id="port-table")

            yield Static(id="notification")

        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize on app mount."""
        # Focus the table to ensure bindings show in footer
        table = self.query_one("#port-table", PortTable)
        table.focus()
        self.do_scan()
        self.start_auto_refresh()
    
    def start_auto_refresh(self) -> None:
        """Start the auto-refresh timer."""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.stop()
        self.auto_refresh_timer = self.set_interval(
            self.refresh_rate, 
            self.do_scan,
            name="auto_refresh"
        )
    
    def do_scan(self) -> None:
        """Start a port scan - sets UI state and triggers background worker."""
        logger.debug("Initiating port scan")
        header = self.query_one("#portwatch-header", PortWatchHeader)
        header.is_scanning = True
        self._run_scan_worker()

    @work(exclusive=True, thread=True)
    def _run_scan_worker(self) -> None:
        """Perform port scan in background thread."""
        ports, error = scan_ports()

        if error:
            logger.warning("Scan completed with error: %s", error)
        else:
            logger.debug("Scan completed successfully, found %d ports", len(ports))

        # Update UI in main thread
        self.call_from_thread(self._update_ports, ports, error)
    
    def _update_ports(self, ports: list[PortInfo], error: str | None = None) -> None:
        """Update the port table with new data."""
        self.ports = ports

        table = self.query_one("#port-table", PortTable)
        table.ports = ports

        header = self.query_one("#portwatch-header", PortWatchHeader)
        header.port_count = len(ports)
        header.refresh_rate = self.refresh_rate
        header.is_scanning = False

        # Show error notification if scan failed
        if error:
            self.show_notification(error, is_error=True)
    
    def show_notification(self, message: str, is_error: bool = False) -> None:
        """Show a notification message."""
        notif = self.query_one("#notification", Static)
        notif.update(f"  {'✗' if is_error else '✓'} {message}")
        notif.remove_class("success", "error")
        notif.add_class("visible", "error" if is_error else "success")
        
        # Auto-hide after 3 seconds
        self.set_timer(3.0, lambda: notif.remove_class("visible"))
    
    def get_selected_port(self) -> PortInfo | None:
        """Get the currently selected port."""
        table = self.query_one("#port-table", PortTable)
        return table.get_selected_port()
    
    # ─── Actions ────────────────────────────────────────────────────────────────
    
    def action_refresh(self) -> None:
        """Manual refresh."""
        self.do_scan()
    
    def action_show_actions(self) -> None:
        """Show action modal for selected port."""
        port = self.get_selected_port()
        if not port:
            self.show_notification("No port selected", is_error=True)
            return
        
        def handle_action(action: str | None) -> None:
            if action == "browser":
                self._do_open_browser(port)
            elif action == "kill":
                self._confirm_kill(port)
            elif action == "copy":
                self._do_copy(port)
        
        self.push_screen(ActionModal(port), handle_action)
    
    def action_open_browser(self) -> None:
        """Open selected port in browser."""
        port = self.get_selected_port()
        if port:
            self._do_open_browser(port)
        else:
            self.show_notification("No port selected", is_error=True)
    
    def action_kill_process(self) -> None:
        """Kill the selected port's process."""
        port = self.get_selected_port()
        if port:
            self._confirm_kill(port)
        else:
            self.show_notification("No port selected", is_error=True)
    
    def action_copy_port(self) -> None:
        """Copy the selected port number."""
        port = self.get_selected_port()
        if port:
            self._do_copy(port)
        else:
            self.show_notification("No port selected", is_error=True)
    
    def action_search(self) -> None:
        """Focus the search input."""
        search_container = self.query_one("#search-container")
        search_container.add_class("visible")
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            table = self.query_one("#port-table", PortTable)
            table.filter_text = event.value

    def action_clear_search(self) -> None:
        """Clear the search filter and hide search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        search_container = self.query_one("#search-container")
        search_container.remove_class("visible")
        table = self.query_one("#port-table", PortTable)
        table.filter_text = ""
        table.focus()
    
    def action_refresh_rate_1(self) -> None:
        self.refresh_rate = 1.0
        self.start_auto_refresh()
        self.show_notification("Refresh rate: 1s")
    
    def action_refresh_rate_2(self) -> None:
        self.refresh_rate = 2.0
        self.start_auto_refresh()
        self.show_notification("Refresh rate: 2s")
    
    def action_refresh_rate_5(self) -> None:
        self.refresh_rate = 5.0
        self.start_auto_refresh()
        self.show_notification("Refresh rate: 5s")
    
    # ─── Action Implementations ─────────────────────────────────────────────────

    def _do_open_browser(self, port: PortInfo) -> None:
        """Open port in browser."""
        logger.debug("Opening browser for port %d", port.port)
        success, msg = open_in_browser(port.port)
        if success:
            logger.debug("Browser opened successfully for port %d", port.port)
        else:
            logger.warning("Failed to open browser for port %d: %s", port.port, msg)
        self.show_notification(msg, is_error=not success)

    def _confirm_kill(self, port: PortInfo) -> None:
        """Show kill confirmation dialog."""
        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self._do_kill(port)

        self.push_screen(ConfirmKillModal(port), handle_confirm)

    def _do_kill(self, port: PortInfo) -> None:
        """Kill the process."""
        if not port.pid:
            logger.warning("Attempted to kill process with no PID for port %d", port.port)
            self.show_notification("No PID to kill", is_error=True)
            return

        logger.debug("Attempting to kill process PID %d (port %d)", port.pid, port.port)
        success, msg = kill_process(port.pid)
        if success:
            logger.debug("Successfully killed process PID %d", port.pid)
        else:
            logger.warning("Failed to kill process PID %d: %s", port.pid, msg)
        self.show_notification(msg, is_error=not success)

        if success:
            # Refresh after kill
            self.set_timer(0.5, self.do_scan)

    def _do_copy(self, port: PortInfo) -> None:
        """Copy port to clipboard."""
        logger.debug("Copying port %d to clipboard", port.port)
        success, msg = copy_to_clipboard(str(port.port))
        if success:
            logger.debug("Port %d copied to clipboard", port.port)
        else:
            logger.warning("Failed to copy port %d to clipboard: %s", port.port, msg)
        self.show_notification(msg, is_error=not success)


def main():
    app = PortWatchApp()
    app.run()


if __name__ == "__main__":
    main()
