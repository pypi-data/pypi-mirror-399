"""
Main port list widget with tactical styling.
"""

from textual.widgets import DataTable
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text

from portwatch.scanner import PortInfo, get_service_hint


# Minimal monochrome - all categories use same muted palette
CATEGORY_COLORS = {
    'web': '#e0e0e0',       # Primary white
    'database': '#e0e0e0',  # Primary white
    'queue': '#e0e0e0',     # Primary white
    'devtool': '#e0e0e0',   # Primary white
    'system': '#666666',    # Muted gray
    'unknown': '#f5a623',   # Amber for unknown only
}

CATEGORY_ICONS = {
    'web': '›',
    'database': '›',
    'queue': '›',
    'devtool': '›',
    'system': '›',
    'unknown': '?',
}


class PortTable(DataTable):
    """
    Tactical port display table with category grouping.
    """

    # Define bindings here so they show in Footer when table is focused
    BINDINGS = [
        Binding("q", "app.quit", "Quit", show=True),
        Binding("r", "app.refresh", "Refresh", show=True),
        Binding("enter", "app.show_actions", "Actions", show=True, priority=True),
        Binding("b", "app.open_browser", "Browser", show=True),
        Binding("k", "app.kill_process", "Kill", show=True),
        Binding("c", "app.copy_port", "Copy", show=True),
        Binding("slash", "app.search", "Search", show=True, key_display="/"),
    ]

    ports: reactive[list[PortInfo]] = reactive(list, always_update=True)
    filter_text: reactive[str] = reactive("", always_update=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self._current_category = None
    
    def on_mount(self) -> None:
        """Set up table columns."""
        self.add_column("", key="status", width=3)
        self.add_column("PORT", key="port", width=7)
        self.add_column("STATUS", key="state", width=8)
        self.add_column("PROCESS", key="process", width=16)
        self.add_column("PID", key="pid", width=8)
        self.add_column("SERVICE", key="service", width=20)
        self.add_column("UPTIME", key="uptime", width=10)
        self.add_column("MEM", key="memory", width=8)
    
    def watch_ports(self, ports: list[PortInfo]) -> None:
        """React to port list changes."""
        self._refresh_table(self._get_filtered_ports())

    def watch_filter_text(self, filter_text: str) -> None:
        """React to filter text changes."""
        self._refresh_table(self._get_filtered_ports())

    def _get_filtered_ports(self) -> list[PortInfo]:
        """Return ports filtered by the current filter_text."""
        if not self.filter_text:
            return self.ports

        search = self.filter_text.lower()
        filtered = []
        for port in self.ports:
            # Match against: port number, process name, service name, category
            port_str = str(port.port)
            process_name = (port.process_name or "").lower()
            service = get_service_hint(port.port, port.process_name).lower()
            category = port.category.lower()
            category_label = port.category_label.lower()
            cmdline = (port.cmdline or "").lower()

            if (search in port_str or
                search in process_name or
                search in service or
                search in category or
                search in category_label or
                search in cmdline):
                filtered.append(port)

        return filtered
    
    def _refresh_table(self, ports: list[PortInfo]) -> None:
        """Rebuild the table with current port data."""
        # Store current selection
        current_row = self.cursor_row

        self.clear()
        self._current_category = None

        for port_info in ports:
            # Add category header if new category
            if port_info.category_label != self._current_category:
                self._current_category = port_info.category_label
                self._add_category_header(port_info.category, port_info.category_label)

            self._add_port_row(port_info)

        # Restore selection if possible, ensuring we're on a port row not a header
        if self.row_count > 0:
            if current_row is not None and current_row < self.row_count:
                self.cursor_coordinate = (current_row, 0)
            # If cursor is on a header row, move to next row (first port)
            self._ensure_cursor_on_port_row()
    
    def _add_category_header(self, category: str, label: str) -> None:
        """Add a category header row - minimal style."""
        color = '#666666'  # Muted for headers
        icon = CATEGORY_ICONS.get(category, '›')

        header_text = Text()
        header_text.append(f"{icon} ", style=f"{color}")
        header_text.append(f"{label.lower()}", style=f"bold {color}")

        # Add as a spanning row (using empty cells for other columns)
        self.add_row(
            "",
            header_text,
            "", "", "", "", "", "",
            key=f"header_{category}",
        )
    
    def _add_port_row(self, port: PortInfo) -> None:
        """Add a port data row - minimal style."""
        # Status indicator - subtle
        if port.status == 'LISTEN':
            status = Text("●", style="#6c8ebf")
        else:
            status = Text("○", style="dim #333333")

        # Port number - clean
        port_text = Text(f":{port.port}", style="#e0e0e0")

        # State - muted
        state_text = Text(port.status.lower(), style="dim #666666")

        # Process name
        proc_name = port.process_name or "—"
        if port.is_docker:
            proc_text = Text(f"{proc_name[:14]}", style="#6c8ebf")
        else:
            proc_text = Text(proc_name[:14], style="#e0e0e0")

        # PID
        pid_text = Text(str(port.pid) if port.pid else "—", style="dim #666666")

        # Service hint / cmdline
        service = get_service_hint(port.port, port.process_name)
        if port.cmdline:
            # Show abbreviated cmdline
            cmd_short = port.cmdline[:25] + "…" if len(port.cmdline) > 25 else port.cmdline
            service_text = Text(cmd_short, style="dim #666666 italic")
        else:
            service_text = Text(service, style="dim #666666")

        # Uptime
        uptime_text = Text(port.uptime, style="dim #666666")

        # Memory - only amber for high usage
        if port.memory_mb > 0:
            if port.memory_mb > 500:
                mem_style = "#f5a623"  # Amber warning
            elif port.memory_mb > 100:
                mem_style = "#e0e0e0"
            else:
                mem_style = "dim #666666"
            mem_text = Text(f"{port.memory_mb:.0f}MB", style=mem_style)
        else:
            mem_text = Text("—", style="dim #666666")

        self.add_row(
            status,
            port_text,
            state_text,
            proc_text,
            pid_text,
            service_text,
            uptime_text,
            mem_text,
            key=f"port_{port.port}",
        )

    def _ensure_cursor_on_port_row(self) -> None:
        """Move cursor to next port row if currently on a header row."""
        if self.cursor_row is None or self.row_count == 0:
            return

        # Get the row key from cursor coordinate (not get_row_at which returns cell values)
        cell_key = self.coordinate_to_cell_key(self.cursor_coordinate)
        row_key = cell_key.row_key.value  # .value gets the actual key string
        if row_key.startswith("header_"):
            # On a header row, move to next row if it exists
            next_row = self.cursor_row + 1
            if next_row < self.row_count:
                self.cursor_coordinate = (next_row, 0)

    def get_selected_port(self) -> PortInfo | None:
        """Get the currently selected port info."""
        if self.cursor_row is None or self.row_count == 0:
            return None

        # Get the row key from cursor coordinate (not get_row_at which returns cell values)
        cell_key = self.coordinate_to_cell_key(self.cursor_coordinate)
        row_key = cell_key.row_key.value  # .value gets the actual key string
        if row_key.startswith("port_"):
            # Find the port in our data (search filtered ports first, then all)
            port_num = int(row_key.replace("port_", ""))
            filtered_ports = self._get_filtered_ports()
            for port in filtered_ports:
                if port.port == port_num:
                    return port
            # Fallback to all ports
            for port in self.ports:
                if port.port == port_num:
                    return port
        return None
