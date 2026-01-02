"""
Actions for port management - kill processes, open browser, etc.
"""

import subprocess
import sys
import webbrowser

import psutil


def kill_process(pid: int, force: bool = False) -> tuple[bool, str]:
    """
    Kill a process by PID.
    
    Returns (success, message).
    """
    if not pid:
        return False, "No PID provided"
    
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        
        if force:
            proc.kill()  # SIGKILL
            action = "Force killed"
        else:
            proc.terminate()  # SIGTERM
            action = "Terminated"
        
        # Wait briefly for process to end
        try:
            proc.wait(timeout=2)
        except psutil.TimeoutExpired:
            if not force:
                # Try force kill
                proc.kill()
                action = "Force killed (after timeout)"
        
        return True, f"{action} {proc_name} (PID {pid})"
        
    except psutil.NoSuchProcess:
        return False, f"Process {pid} no longer exists"
    except psutil.AccessDenied:
        return False, f"Permission denied to kill PID {pid}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def open_in_browser(port: int, https: bool = False) -> tuple[bool, str]:
    """
    Open localhost:port in the default browser.
    
    Returns (success, message).
    """
    protocol = "https" if https else "http"
    url = f"{protocol}://localhost:{port}"
    
    try:
        webbrowser.open(url)
        return True, f"Opened {url}"
    except Exception as e:
        return False, f"Failed to open browser: {str(e)}"


def copy_to_clipboard(text: str) -> tuple[bool, str]:
    """
    Copy text to system clipboard.
    
    Returns (success, message).
    """
    try:
        if sys.platform == 'darwin':
            # macOS
            subprocess.run(['pbcopy'], input=text.encode(), check=True)
        elif sys.platform == 'linux':
            # Linux - try xclip first, then xsel
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], 
                             input=text.encode(), check=True)
            except FileNotFoundError:
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'], 
                                 input=text.encode(), check=True)
                except FileNotFoundError:
                    return False, "Install xclip or xsel for clipboard support"
        elif sys.platform == 'win32':
            # Windows - use shell=False for security (avoids shell injection)
            subprocess.run(['clip'], input=text.encode(), check=True)
        else:
            return False, f"Unsupported platform: {sys.platform}"
        
        return True, f"Copied to clipboard: {text}"
        
    except subprocess.CalledProcessError as e:
        return False, f"Clipboard error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_process_details(pid: int) -> dict | None:
    """
    Get detailed information about a process.
    """
    if not pid:
        return None
    
    try:
        proc = psutil.Process(pid)
        
        return {
            'pid': pid,
            'name': proc.name(),
            'cmdline': ' '.join(proc.cmdline()),
            'user': proc.username(),
            'cpu_percent': proc.cpu_percent(interval=0.1),
            'memory_mb': proc.memory_info().rss / (1024 * 1024),
            'memory_percent': proc.memory_percent(),
            'num_threads': proc.num_threads(),
            'create_time': proc.create_time(),
            'status': proc.status(),
            'cwd': proc.cwd() if hasattr(proc, 'cwd') else None,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
        return None
