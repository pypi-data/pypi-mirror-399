"""
Action modal for port operations.
"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label

from portwatch.scanner import PortInfo, get_service_hint


class ActionModal(ModalScreen[str | None]):
    """
    Modal dialog showing port details and available actions.
    """
    
    CSS = """
    ActionModal {
        align: center middle;
    }

    #modal-container {
        width: 50;
        height: auto;
        max-height: 80%;
        background: #0a0a0a;
        border: solid #1e1e1e;
        padding: 1 2;
    }

    #modal-header {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid #1e1e1e;
        margin-bottom: 1;
    }

    #details-grid {
        grid-size: 2;
        grid-columns: 10 1fr;
        grid-rows: auto;
        padding: 1 0;
    }

    .detail-label {
        color: #666666;
    }

    .detail-value {
        color: #e0e0e0;
    }

    #divider {
        margin: 1 0;
        color: #1e1e1e;
    }

    #actions-container {
        padding-top: 1;
    }

    .action-row {
        height: 3;
        margin-bottom: 0;
    }

    Button {
        width: 100%;
        background: #1e1e1e;
        color: #e0e0e0;
        border: none;
    }

    Button:hover {
        background: #2a2a2a;
    }

    Button.action-browser {
        background: #1e1e1e;
    }

    Button.action-kill {
        background: #1e1e1e;
        color: #d64545;
    }

    Button.action-copy {
        background: #1e1e1e;
    }

    Button.action-close {
        background: #141414;
        color: #666666;
    }

    #keybinds {
        text-align: center;
        color: #666666;
        padding-top: 1;
    }
    """
    
    BINDINGS = [
        ("escape", "close", "Close"),
        ("b", "browser", "Browser"),
        ("k", "kill", "Kill"),
        ("c", "copy", "Copy"),
    ]
    
    def __init__(self, port_info: PortInfo, **kwargs):
        super().__init__(**kwargs)
        self.port_info = port_info
    
    def compose(self) -> ComposeResult:
        port = self.port_info
        service = get_service_hint(port.port, port.process_name)
        
        with Vertical(id="modal-container"):
            # Header - minimal
            yield Static(
                f"[bold #e0e0e0]:{port.port}[/]  [dim #666666]{port.process_name or 'unknown'}[/]",
                id="modal-header"
            )
            
            # Details grid
            with Grid(id="details-grid"):
                yield Label("PID:", classes="detail-label")
                yield Label(str(port.pid) if port.pid else "—", classes="detail-value")
                
                yield Label("User:", classes="detail-label")
                yield Label(port.user or "—", classes="detail-value")
                
                yield Label("Service:", classes="detail-label")
                yield Label(service, classes="detail-value")
                
                yield Label("CPU:", classes="detail-label")
                yield Label(f"{port.cpu_percent:.1f}%", classes="detail-value")
                
                yield Label("Memory:", classes="detail-label")
                yield Label(f"{port.memory_mb:.1f} MB", classes="detail-value")
                
                yield Label("Uptime:", classes="detail-label")
                yield Label(port.uptime, classes="detail-value")
                
                if port.cmdline:
                    yield Label("Command:", classes="detail-label")
                    cmd_display = port.cmdline[:40] + "…" if len(port.cmdline) > 40 else port.cmdline
                    yield Label(cmd_display, classes="detail-value")
            
            yield Static("", id="divider")

            # Action buttons - minimal
            with Vertical(id="actions-container"):
                with Horizontal(classes="action-row"):
                    yield Button(
                        "Open in Browser  b",
                        id="btn-browser",
                        classes="action-browser",
                    )

                with Horizontal(classes="action-row"):
                    yield Button(
                        "Kill Process  k",
                        id="btn-kill",
                        classes="action-kill",
                    )

                with Horizontal(classes="action-row"):
                    yield Button(
                        "Copy Port  c",
                        id="btn-copy",
                        classes="action-copy",
                    )

                with Horizontal(classes="action-row"):
                    yield Button(
                        "Close  esc",
                        id="btn-close",
                        classes="action-close",
                    )

            yield Static("[dim #666666]press key or click[/]", id="keybinds")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "btn-browser":
            self.dismiss("browser")
        elif button_id == "btn-kill":
            self.dismiss("kill")
        elif button_id == "btn-copy":
            self.dismiss("copy")
        elif button_id == "btn-close":
            self.dismiss(None)
    
    def action_close(self) -> None:
        self.dismiss(None)
    
    def action_browser(self) -> None:
        self.dismiss("browser")
    
    def action_kill(self) -> None:
        self.dismiss("kill")
    
    def action_copy(self) -> None:
        self.dismiss("copy")


class ConfirmKillModal(ModalScreen[bool]):
    """Confirmation dialog for killing a process."""

    CSS = """
    ConfirmKillModal {
        align: center middle;
    }

    #confirm-container {
        width: 40;
        height: auto;
        background: #0a0a0a;
        border: solid #d64545;
        padding: 1 2;
    }

    #confirm-header {
        text-align: center;
        padding-bottom: 1;
    }

    #confirm-message {
        text-align: center;
        padding: 1 0;
        color: #e0e0e0;
    }

    #confirm-buttons {
        padding-top: 1;
    }

    #confirm-buttons Button {
        width: 50%;
        background: #1e1e1e;
    }

    #confirm-buttons #btn-yes {
        color: #d64545;
    }

    #confirm-buttons #btn-no {
        color: #666666;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def __init__(self, port_info: PortInfo, **kwargs):
        super().__init__(**kwargs)
        self.port_info = port_info

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-container"):
            yield Static(
                "[#d64545]Kill process?[/]",
                id="confirm-header"
            )
            yield Static(
                f"[#e0e0e0]{self.port_info.process_name}[/] on :{self.port_info.port}\n"
                f"[dim #666666]pid {self.port_info.pid}[/]",
                id="confirm-message"
            )
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes  y", id="btn-yes")
                yield Button("No  n", id="btn-no")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_confirm(self) -> None:
        self.dismiss(True)
    
    def action_cancel(self) -> None:
        self.dismiss(False)
