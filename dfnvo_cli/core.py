import typer
import httpx
import os
import json
from typing import Dict
from datetime import datetime, timedelta

app = typer.Typer()

# Configuration
API_BASE_URL = "http://localhost/api"
# API_BASE_URL = "http://dev-vo.dfn.net.au/api"
CONFIG_FILE = os.path.expanduser("~/.dfn_vo_config.json")


def save_user_data(user_data: Dict):
    """Save the user data and access token to a config file."""
    user_data['token_expiry'] = (
        datetime.now() + timedelta(hours=24)).isoformat()
    with open(CONFIG_FILE, "w") as f:
        json.dump(user_data, f)
    typer.echo(f"Debug: Saved user data to {CONFIG_FILE}")


def load_user_data() -> Dict:
    """Load the user data from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            typer.echo(f"Debug: Loaded user data from {CONFIG_FILE}")
            return data
    typer.echo(f"Debug: No user data found at {CONFIG_FILE}")
    return {}


def get_headers() -> Dict:
    """Get headers including the access token if available."""
    user_data = load_user_data()
    if user_data and "access_token" in user_data:
        return {"Authorization": f"Bearer {user_data['access_token']}"}
    return {}


def is_token_valid() -> bool:
    """Check if the stored token is still valid."""
    user_data = load_user_data()
    if not user_data or "access_token" not in user_data:
        typer.echo("Debug: No token found in user data")
        return False

    # For now, let's just check if we have a token
    # In a production environment, you'd want to validate this token with your server
    typer.echo("Debug: Token found in user data")
    return True


@app.command()
def login(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force login even if already logged in")
):
    """Log in to the DFN VO application."""
    if not force and is_token_valid():
        user_data = load_user_data()
        typer.echo(
            f"You are already logged in as {user_data['user']['email']}.")
        typer.echo("Use --force to login again if needed.")
        return

    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True)

    try:
        response = httpx.post(
            f"{API_BASE_URL}/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        user_data = response.json()
        save_user_data(user_data)
        typer.echo(
            f"Login successful! Welcome, {user_data['user']['first_name']} {user_data['user']['last_name']}.")
    except httpx.HTTPStatusError as e:
        typer.echo(f"Login failed: {e.response.text}")
    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}")


@app.command()
def logout():
    """Log out from the DFN VO application."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        typer.echo("Logged out successfully.")
    else:
        typer.echo("You were not logged in.")


@app.command()
def user_info():
    """Display current user information."""
    if not is_token_valid():
        typer.echo(
            "You are not logged in or your session has expired. Please login first.")
        return

    user_data = load_user_data()
    if "user" not in user_data:
        typer.echo("Debug: User data is incomplete")
        typer.echo(
            f"Debug: Contents of user_data: {json.dumps(user_data, indent=2)}")
        typer.echo(
            "Error: User information is not available. Please try logging in again.")
        return

    user = user_data["user"]
    typer.echo(f"User ID: {user.get('user_id', 'N/A')}")
    typer.echo(
        f"Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
    typer.echo(f"Email: {user.get('email', 'N/A')}")
    typer.echo(
        f"Active Status: {'Active' if user.get('active_status') else 'Inactive'}")
    typer.echo(f"Admin: {'Yes' if user.get('is_admin') else 'No'}")


if __name__ == "__main__":
    app()
