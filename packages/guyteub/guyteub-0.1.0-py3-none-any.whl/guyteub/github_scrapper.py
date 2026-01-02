import requests
from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from datetime import datetime

console = Console()

def parse_date(date_str):
    """Parse la date dans un format lisible"""
    if not date_str:
        return "Non disponible"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d/%m/%Y à %H:%M")
    except:
        return date_str

def format_number(num):
    """Format numbers with K/M suffixes for better readability"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def create_stat_card(label, value, icon, color="cyan"):
    """Create a beautiful stat card with icon and large value"""
    stat_text = Text()
    stat_text.append(f"{icon}\n", style=f"bold {color}")
    stat_text.append(f"{format_number(value)}\n", style=f"bold {color}")
    stat_text.append(label, style=f"dim {color}")
    stat_text.justify = "center"

    return Panel(
        stat_text,
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 0),
        expand=True
    )

def create_profile_header(data):
    """Create the profile header section"""
    username = data.get('login', 'Unknown')
    name = data.get('name', username)
    bio = data.get('bio', 'No bio available')

    header_text = Text()
    header_text.append(f"👤 {name}\n", style="bold bright_white on blue")
    header_text.append(f"@{username}\n", style="dim cyan")
    if bio and bio != 'No bio available':
        header_text.append(f"\n{bio}", style="italic white")

    return Panel(
        Align.center(header_text),
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(0, 1),
        title="[bold bright_white]GitHub Profile[/bold bright_white]",
        title_align="left",
        expand=True
    )

def create_info_section(data):
    """Create personal information section"""
    info_items = []

    # GitHub Profile URL
    if data.get('html_url'):
        info_items.append(f"🔗 {data.get('html_url')}")

    # Company
    if data.get('company'):
        info_items.append(f"🏢 {data.get('company')}")

    # Location
    if data.get('location'):
        info_items.append(f"📍 {data.get('location')}")

    # Email
    if data.get('email'):
        info_items.append(f"📧 {data.get('email')}")

    # Blog
    if data.get('blog'):
        info_items.append(f"🌐 {data.get('blog')}")

    # Twitter
    if data.get('twitter_username'):
        info_items.append(f"🐦 @{data.get('twitter_username')}")

    # Hireable status
    hireable = data.get('hireable')
    if hireable:
        info_items.append("✅ Hireable")

    info_text = "\n".join(info_items) if info_items else "No additional information"

    # Ensure minimum height matches other panels (4 lines like metadata and stats)
    current_lines = len(info_items)
    if current_lines < 4:
        info_items.extend([""] * (4 - current_lines))
        info_text = "\n".join(info_items)

    return Panel(
        Text(info_text, overflow="fold"),
        title="[bold cyan]ℹ️  Info[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )

def create_metadata_table(data):
    """Create a clean metadata table"""
    # Create a text-based metadata display instead of a table for better wrapping
    metadata_lines = []
    metadata_lines.append(f"[dim cyan]🆔 ID:[/dim cyan] {data.get('id', 'N/A')}")
    metadata_lines.append(f"[dim cyan]👤 Type:[/dim cyan] {data.get('type', 'User')}")
    metadata_lines.append(f"[dim cyan]📅 Joined:[/dim cyan] {parse_date(data.get('created_at'))}")
    metadata_lines.append(f"[dim cyan]🔄 Updated:[/dim cyan] {parse_date(data.get('updated_at'))}")

    metadata_text = "\n".join(metadata_lines)

    return Panel(
        metadata_text,
        title="[bold yellow]📋 Metadata[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )

def create_repos_table(repos):
    """Create a compact repositories table"""
    table = Table(
        box=box.SIMPLE_HEAD,
        padding=(0, 1),
        show_header=True,
        header_style="bold bright_magenta",
        expand=True
    )

    table.add_column("Nom", style="cyan", no_wrap=True)
    table.add_column("Lien GitHub", style="blue")
    table.add_column("⭐", style="bright_yellow", justify="right")
    table.add_column("Langage", style="bright_green")

    # Limiter à 10 repos et trier par stars
    sorted_repos = sorted(repos, key=lambda r: r.get('stargazers_count', 0), reverse=True)[:10]

    for repo in sorted_repos:
        name = repo.get('name', 'N/A')
        github_url = repo.get('html_url', 'N/A')
        stars = format_number(repo.get('stargazers_count', 0))
        lang = repo.get('language', '-')

        table.add_row(name, github_url, stars, lang)

    return Panel(
        table,
        title="[bold bright_magenta]📦 Repositories[/bold bright_magenta]",
        border_style="bright_magenta",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )

def scrapper(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Header section - full width with centered content
        header = create_profile_header(data)

        # Information sections
        info_section = create_info_section(data)
        metadata_section = create_metadata_table(data)

        # Stats section - text-based for better readability
        stats_lines = []
        stats_lines.append(f"[dim cyan]📦 Repos:[/dim cyan] {format_number(data.get('public_repos', 0))}")
        stats_lines.append(f"[dim cyan]👥 Followers:[/dim cyan] {format_number(data.get('followers', 0))}")
        stats_lines.append(f"[dim cyan]➕ Following:[/dim cyan] {format_number(data.get('following', 0))}")
        stats_lines.append(f"[dim cyan]📝 Gists:[/dim cyan] {format_number(data.get('public_gists', 0))}")

        stats_text = "\n".join(stats_lines)

        stats_panel = Panel(
            stats_text,
            title="[bold bright_magenta]📊 Stats[/bold bright_magenta]",
            border_style="bright_magenta",
            box=box.ROUNDED,
            padding=(0, 1),
            expand=True
        )

        # Create a container table for the three panels in a row
        container = Table.grid(expand=True, padding=(0, 1))
        container.add_column(ratio=1)
        container.add_column(ratio=1)
        container.add_column(ratio=1)
        container.add_row(info_section, metadata_section, stats_panel)

        # Fetch repositories
        repos_url = f"https://api.github.com/users/{username}/repos"
        repos_response = requests.get(repos_url)
        repos_panel = None
        if repos_response.status_code == 200:
            repos = repos_response.json()
            if repos:
                repos_panel = create_repos_table(repos)

        # Print everything compactly
        console.print(header)
        console.print(container)
        if repos_panel:
            console.print(repos_panel)

    else:
        # Enhanced error display
        error_panel = Panel(
            f"[bold red]❌ Error {response.status_code}[/bold red]\n\n"
            f"User '[cyan]{username}[/cyan]' not found.\n\n"
            f"[dim]Please verify the username and try again.[/dim]",
            title="[bold red]⚠️  Request Failed[/bold red]",
            border_style="red",
            box=box.HEAVY,
            padding=(0, 1)
        )
        console.print(error_panel)