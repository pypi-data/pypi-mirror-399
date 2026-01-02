"""
Port scanning and process detection logic.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
import subprocess
import re
import psutil

# Create logger for this module
logger = logging.getLogger("portwatch.scanner")


@dataclass
class PortInfo:
    """Information about a listening port."""
    port: int
    protocol: str = "tcp"
    status: str = "LISTEN"
    pid: int | None = None
    process_name: str | None = None
    cmdline: str | None = None
    user: str | None = None
    category: str = "unknown"
    category_label: str = "UNKNOWN"
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    create_time: datetime | None = None
    is_docker: bool = False
    container_name: str | None = None
    connections: int = 0

    @property
    def uptime(self) -> str:
        """Human-readable uptime."""
        if not self.create_time:
            return "—"
        delta = datetime.now() - self.create_time
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        elif seconds < 86400:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"


# Known port → category mappings
PORT_CATEGORIES = {
    # Web Servers
    80: ("web", "WEB SERVERS"),
    443: ("web", "WEB SERVERS"),
    3000: ("web", "WEB SERVERS"),
    3001: ("web", "WEB SERVERS"),
    4000: ("web", "WEB SERVERS"),
    5000: ("web", "WEB SERVERS"),
    5173: ("web", "WEB SERVERS"),  # Vite
    5174: ("web", "WEB SERVERS"),
    8000: ("web", "WEB SERVERS"),
    8080: ("web", "WEB SERVERS"),
    8888: ("web", "WEB SERVERS"),
    9000: ("web", "WEB SERVERS"),
    
    # Databases
    5432: ("database", "DATABASES"),
    3306: ("database", "DATABASES"),
    6379: ("database", "DATABASES"),
    27017: ("database", "DATABASES"),
    9200: ("database", "DATABASES"),  # Elasticsearch
    9300: ("database", "DATABASES"),
    5984: ("database", "DATABASES"),  # CouchDB
    7474: ("database", "DATABASES"),  # Neo4j
    8529: ("database", "DATABASES"),  # ArangoDB
    26257: ("database", "DATABASES"),  # CockroachDB
    
    # Message Queues
    5672: ("queue", "MESSAGE QUEUES"),
    15672: ("queue", "MESSAGE QUEUES"),  # RabbitMQ Management
    9092: ("queue", "MESSAGE QUEUES"),  # Kafka
    2181: ("queue", "MESSAGE QUEUES"),  # Zookeeper
    4222: ("queue", "MESSAGE QUEUES"),  # NATS
    
    # Dev Tools
    5555: ("devtool", "DEV TOOLS"),  # Flower
    8025: ("devtool", "DEV TOOLS"),  # MailHog
    1025: ("devtool", "DEV TOOLS"),  # MailHog SMTP
    8081: ("devtool", "DEV TOOLS"),
    9090: ("devtool", "DEV TOOLS"),  # Prometheus
    3100: ("devtool", "DEV TOOLS"),  # Loki
    16686: ("devtool", "DEV TOOLS"),  # Jaeger
    
    # System
    22: ("system", "SYSTEM"),
    53: ("system", "SYSTEM"),  # DNS
    631: ("system", "SYSTEM"),  # CUPS
}


SERVICE_NAMES = {
    80: "HTTP",
    443: "HTTPS",
    3000: "Node.js",
    3001: "Node.js",
    4000: "Dev Server",
    5000: "Flask/Dev",
    5173: "Vite",
    5174: "Vite",
    8000: "Django",
    8080: "HTTP Alt",
    8888: "Jupyter",
    9000: "PHP-FPM",
    5432: "PostgreSQL",
    3306: "MySQL",
    6379: "Redis",
    27017: "MongoDB",
    9200: "Elasticsearch",
    5672: "RabbitMQ",
    15672: "RabbitMQ UI",
    9092: "Kafka",
    5555: "Flower",
    8025: "MailHog",
    22: "SSH",
    53: "DNS",
}


def categorize_port(port: int) -> tuple[str, str]:
    """Return (category, category_label) for a port."""
    return PORT_CATEGORIES.get(port, ("unknown", "OTHER"))


def get_service_hint(port: int, process_name: str | None) -> str:
    """Get a service hint for display."""
    if port in SERVICE_NAMES:
        return SERVICE_NAMES[port]
    return process_name or "unknown"


def scan_ports_lsof() -> tuple[list[PortInfo], str | None]:
    """
    Scan listening ports using lsof command (macOS fallback).

    This function uses `lsof -iTCP -sTCP:LISTEN -n -P` which works without
    sudo for user-owned processes on macOS.

    Returns:
        A tuple of (ports, error_message) where:
        - ports: List of PortInfo objects for each listening port found
        - error_message: None on success, or an error string if something went wrong
    """
    logger.debug("Starting port scan using lsof fallback method")
    ports: list[PortInfo] = []
    seen_ports: set[int] = set()

    try:
        # Run lsof to get listening TCP ports
        # -iTCP: Only TCP connections
        # -sTCP:LISTEN: Only listening sockets
        # -n: Don't resolve hostnames (faster)
        # -P: Don't resolve port names (show numbers)
        result = subprocess.run(
            ['lsof', '-iTCP', '-sTCP:LISTEN', '-n', '-P'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0 and not result.stdout:
            # lsof returns 1 if no results, but may still have output
            if result.stderr:
                return ([], f"lsof error: {result.stderr.strip()}")
            return ([], None)  # No listening ports found

        # Parse lsof output
        # Example format:
        # COMMAND   PID   USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
        # postgres  1234  mal    5u   IPv4  0x...  0t0      TCP  *:5432 (LISTEN)
        # node      5678  mal    22u  IPv6  0x...  0t0      TCP  *:3000 (LISTEN)

        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return ([], None)  # Only header or empty

        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue

            # Parse the line - fields are space-separated but command can have spaces
            # Use regex to extract the key fields we need
            parts = line.split()
            if len(parts) < 9:
                continue

            process_name = parts[0]
            try:
                pid = int(parts[1])
            except ValueError:
                continue

            user = parts[2]

            # The NAME column is the last part and contains the port
            # Format: *:PORT (LISTEN) or 127.0.0.1:PORT (LISTEN) or [::1]:PORT (LISTEN)
            name_col = parts[-2] if parts[-1] == '(LISTEN)' else parts[-1]

            # Extract port number from the NAME column
            # Handle formats: *:5432, 127.0.0.1:3000, [::1]:8080
            port_match = re.search(r':(\d+)$', name_col.replace('(LISTEN)', '').strip())
            if not port_match:
                continue

            try:
                port = int(port_match.group(1))
            except ValueError:
                continue

            # Skip duplicates
            if port in seen_ports:
                continue
            seen_ports.add(port)

            # Get additional process info using psutil if possible
            cmdline = None
            cpu = 0.0
            mem_mb = 0.0
            create_time = None
            is_docker = False

            try:
                proc = psutil.Process(pid)

                # Get cmdline (truncated)
                try:
                    cmd_parts = proc.cmdline()
                    if cmd_parts:
                        cmdline = ' '.join(cmd_parts)[:60]
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                # Check if Docker
                is_docker = 'docker' in process_name.lower() or 'containerd' in process_name.lower()

                try:
                    cpu = proc.cpu_percent(interval=0.01)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                try:
                    mem_info = proc.memory_info()
                    mem_mb = mem_info.rss / (1024 * 1024)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                try:
                    create_time = datetime.fromtimestamp(proc.create_time())
                except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                    pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            cat, cat_label = categorize_port(port)

            ports.append(PortInfo(
                port=port,
                protocol='tcp',
                status='LISTEN',
                pid=pid,
                process_name=process_name,
                cmdline=cmdline,
                user=user,
                category=cat,
                category_label=cat_label,
                cpu_percent=cpu,
                memory_mb=mem_mb,
                create_time=create_time,
                is_docker=is_docker,
            ))

        # Sort by category then port
        category_order = ['web', 'database', 'queue', 'devtool', 'system', 'unknown']
        sorted_ports = sorted(ports, key=lambda p: (category_order.index(p.category) if p.category in category_order else 99, p.port))
        logger.debug("lsof scan complete: found %d listening ports", len(sorted_ports))
        return (sorted_ports, None)

    except subprocess.TimeoutExpired:
        logger.warning("lsof command timed out")
        return ([], "lsof command timed out")
    except FileNotFoundError:
        logger.warning("lsof command not found")
        return ([], "lsof command not found")
    except Exception as e:
        logger.error("lsof error: %s", str(e))
        return ([], f"lsof error: {str(e)}")


def scan_ports() -> tuple[list[PortInfo], str | None]:
    """
    Scan all listening ports and return detailed info.

    First tries the psutil method, then falls back to lsof on macOS
    if psutil returns empty results or permission denied.

    Returns:
        A tuple of (ports, error_message) where:
        - ports: List of PortInfo objects for each listening port found
        - error_message: None on success, or an error string if something went wrong
    """
    logger.debug("Starting port scan using psutil method")
    ports: list[PortInfo] = []
    seen_ports: set[int] = set()
    psutil_error: str | None = None
    use_lsof_fallback = False
    connections = []

    try:
        connections = psutil.net_connections(kind='inet')
        logger.debug("Successfully retrieved network connections via psutil (inet)")
    except psutil.AccessDenied:
        logger.debug("Access denied for inet connections, trying TCP only")
        # Try with TCP only if access denied
        try:
            connections = psutil.net_connections(kind='tcp')
            logger.debug("Successfully retrieved network connections via psutil (tcp)")
        except psutil.AccessDenied:
            logger.debug("psutil permission denied, will try lsof fallback")
            psutil_error = "Permission denied"
            use_lsof_fallback = True
    
    if not use_lsof_fallback:
        for conn in connections:
            # Only interested in listening ports
            if conn.status != 'LISTEN':
                continue

            if not conn.laddr:
                continue

            port = conn.laddr.port

            # Skip duplicates (same port on different interfaces)
            if port in seen_ports:
                continue
            seen_ports.add(port)

            # Get process info
            proc_name = None
            cmdline = None
            user = None
            cpu = 0.0
            mem_mb = 0.0
            create_time = None
            is_docker = False

            if conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    proc_name = proc.name()

                    # Get cmdline (truncated)
                    try:
                        cmd_parts = proc.cmdline()
                        if cmd_parts:
                            cmdline = ' '.join(cmd_parts)[:60]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass

                    # Check if Docker
                    is_docker = 'docker' in proc_name.lower() or 'containerd' in proc_name.lower()

                    try:
                        user = proc.username()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass

                    try:
                        cpu = proc.cpu_percent(interval=0.01)
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass

                    try:
                        mem_info = proc.memory_info()
                        mem_mb = mem_info.rss / (1024 * 1024)
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass

                    try:
                        create_time = datetime.fromtimestamp(proc.create_time())
                    except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                        pass

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.debug("Could not access process info for PID %s: %s", conn.pid, e)

            cat, cat_label = categorize_port(port)

            ports.append(PortInfo(
                port=port,
                protocol='tcp',
                status=conn.status,
                pid=conn.pid,
                process_name=proc_name,
                cmdline=cmdline,
                user=user,
                category=cat,
                category_label=cat_label,
                cpu_percent=cpu,
                memory_mb=mem_mb,
                create_time=create_time,
                is_docker=is_docker,
            ))

        logger.debug("psutil scan complete: found %d listening ports", len(ports))

    # Fallback to lsof if psutil returned empty results or had permission issues
    # This is especially useful on macOS where psutil may not see all ports without sudo
    if use_lsof_fallback or len(ports) == 0:
        logger.debug("Trying lsof fallback (psutil_error=%s, ports_count=%d)", psutil_error, len(ports))
        lsof_ports, lsof_error = scan_ports_lsof()

        if lsof_ports:
            # If psutil got partial results, merge with lsof results
            psutil_port_nums = {p.port for p in ports}
            for lsof_port in lsof_ports:
                if lsof_port.port not in psutil_port_nums:
                    ports.append(lsof_port)
            logger.debug("After lsof merge: %d total ports", len(ports))

        # Only report error if both methods failed
        if len(ports) == 0 and (psutil_error or lsof_error):
            error_msg = psutil_error or lsof_error
            logger.warning("Both psutil and lsof failed: %s", error_msg)
            return ([], f"Unable to scan ports: {error_msg}")

    # Sort by category then port
    category_order = ['web', 'database', 'queue', 'devtool', 'system', 'unknown']
    sorted_ports = sorted(ports, key=lambda p: (category_order.index(p.category) if p.category in category_order else 99, p.port))
    return (sorted_ports, None)


def count_connections(port: int) -> int:
    """Count established connections to a port."""
    count = 0
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.laddr.port == port and conn.status == 'ESTABLISHED':
                count += 1
    except psutil.AccessDenied:
        pass
    return count
