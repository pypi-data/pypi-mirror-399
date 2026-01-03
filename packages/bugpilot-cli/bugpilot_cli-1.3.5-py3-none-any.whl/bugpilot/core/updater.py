"""
Version checking and update functionality
"""

import sys
import subprocess
from packaging import version
import requests

PACKAGE_NAME = "bugpilot-cli"
from bugpilot import __version__ as CURRENT_VERSION

def get_latest_version():
    """Get latest version from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception:
        pass
    return None

def check_for_updates():
    """Check if a newer version is available"""
    try:
        latest = get_latest_version()
        if latest and version.parse(latest) > version.parse(CURRENT_VERSION):
            return latest
    except Exception:
        pass
    return None

def update_package(ui=None):
    """Update the package using pip"""
    try:
        if ui:
            ui.print_info(f"Updating {PACKAGE_NAME}...")
        
        # Run pip install --upgrade
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            latest = get_latest_version()
            if ui:
                ui.print_success(f"✓ Successfully updated to version {latest}!")
                ui.print_warning("Please restart BugPilot to use the new version.")
            return True
        else:
            if ui:
                ui.print_error(f"Update failed: {result.stderr}")
            return False
            
    except Exception as e:
        if ui:
            ui.print_error(f"Update error: {e}")
        return False

def show_update_notification(ui, latest_version):
    """Show update available notification"""
    from rich.panel import Panel
    
    message = f"""
[!] [bold]New version available![/bold]

Current version: [bold]{CURRENT_VERSION}[/bold]
Latest version: [bold]{latest_version}[/bold]

To update, run: `/update`
Or manually: `pip install --upgrade {PACKAGE_NAME}`
"""
    
    ui.console.print(Panel(
        message,
        title="[yellow][!] Update Available[/yellow]",
        border_style="yellow"
    ))
