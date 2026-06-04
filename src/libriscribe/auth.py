#!/usr/bin/env python
"""
Authentication module for LibriScribe
Password: User enters the SHA256 hash directly
Hash is generated from: current_time_HHMM + "suhasdm"
"""

import hashlib
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def generate_password_hash():
    """Generate the correct password hash for current time (5-minute intervals)"""
    now = datetime.now()
    # Round down to nearest 5-minute interval
    minute = (now.minute // 5) * 5
    time_str = f"{now.hour:02d}{minute:02d}"  # HHMM format
    password_string = f"{time_str}suhasdm"
    
    # Create SHA256 hash
    password_hash = hashlib.sha256(password_string.encode()).hexdigest()
    return password_hash

def verify_password(user_input: str) -> bool:
    """Verify if the user's hash input is correct"""
    correct_hash = generate_password_hash()
    # User enters the hash directly, so just compare
    return user_input.strip().lower() == correct_hash.lower()

def authenticate():
    """
    Authenticate user before running LibriScribe commands
    User must enter the SHA256 hash directly
    Returns True if authenticated, False otherwise
    """
    console.print("\n[bold cyan]🔐 LibriScribe Authentication[/bold cyan]")
    console.print("[dim]Enter authentication hash to continue[/dim]\n")
    
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        password_hash = Prompt.ask("[yellow]Hash[/yellow]", password=True)
        
        if verify_password(password_hash):
            console.print("[green]✓ Authentication successful![/green]\n")
            return True
        else:
            remaining = max_attempts - attempt
            if remaining > 0:
                console.print(f"[red]✗ Invalid hash. {remaining} attempt(s) remaining.[/red]\n")
            else:
                console.print("[red]✗ Authentication failed. Access denied.[/red]\n")
    
    return False

def get_current_password_hash():
    """
    Get the current password hash
    (For authorized users only)
    """
    return generate_password_hash()

if __name__ == "__main__":
    # Test the authentication
    console.print("[bold]Testing Authentication System[/bold]\n")
    console.print(f"[dim]Current time: {datetime.now().strftime('%H:%M')}[/dim]")
    console.print(f"[green]Current hash: {get_current_password_hash()}[/green]\n")
    
    if authenticate():
        console.print("[green]Access granted![/green]")
    else:
        console.print("[red]Access denied![/red]")
