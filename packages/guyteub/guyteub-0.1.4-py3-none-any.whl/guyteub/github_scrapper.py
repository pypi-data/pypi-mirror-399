"""
GitHub Profile Scraper
Fetches and displays GitHub user profiles and repository information
"""
import requests
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box


console = Console()


LANGUAGE_ICONS = {
    'Python': '🐍',
    'JavaScript': '🟨',
    'TypeScript': '🔷',
    'Java': '☕',
    'C++': '⚡',
    'C': '🔧',
    'C#': '🎯',
    'Go': '🐹',
    'Rust': '🦀',
    'Ruby': '💎',
    'PHP': '🐘',
    'Swift': '🦅',
    'Kotlin': '🅺',
    'R': '📊',
    'Shell': '🐚',
    'HTML': '🌐',
    'CSS': '🎨',
    'Vue': '💚',
    'React': '⚛️',
    'Dart': '🎯',
    'Scala': '🔴',
    'Perl': '🐪',
    'Lua': '🌙',
    'Haskell': '🎓',
    'Objective-C': '🍎',
    'MATLAB': '📐',
    'Julia': '🟣',
    'Elixir': '💧',
    'Clojure': '☘️',
}


def parse_date(date_str):
    """Parse ISO date string to a human-readable format"""
    if not date_str:
        return "Non disponible"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d/%m/%Y à %H:%M")
    except (ValueError, TypeError):
        return date_str


def format_number(num):
    """Format numbers with K/M suffixes for better readability"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)


def create_profile_header(data):
    """Create the profile header section with user information"""
    username = data.get('login', 'Unknown')
    name = data.get('name', username)
    bio = data.get('bio', 'No bio available')
    url = data.get('html_url', '')

    header_text = Text()
    header_text.append(f"👤 {name}\n", style="bold bright_white")
    if url:
        header_text.append(f"🔗 {url}\n", style="blue")
    if bio and bio != 'No bio available':
        header_text.append(f"\n{bio}", style="italic white")

    return Panel(
        Align.left(header_text, width=None),
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(0, 1),
        title="[bold bright_white]GitHub Profile[/bold bright_white]",
        title_align="left",
        expand=True
    )


def create_info_section(data):
    """Create personal information section with user details"""
    info_items = []

    if data.get('login'):
        info_items.append(f"👤 @{data.get('login')}")
    if data.get('company'):
        info_items.append(f"🏢 {data.get('company')}")
    if data.get('location'):
        info_items.append(f"📍 {data.get('location')}")
    if data.get('email'):
        info_items.append(f"📧 {data.get('email')}")
    if data.get('blog'):
        info_items.append(f"🌐 {data.get('blog')}")
    if data.get('twitter_username'):
        info_items.append(f"🐦 @{data.get('twitter_username')}")
    if data.get('hireable'):
        info_items.append("✅ Hireable")

    info_text = "\n".join(info_items) if info_items else "No additional information"

    # Ensure minimum height consistency (4 lines)
    current_lines = len(info_items)
    if current_lines < 4:
        info_items.extend([""] * (4 - current_lines))
        info_text = "\n".join(info_items)

    return Panel(
        Text(info_text, overflow="ignore", no_wrap=False),
        title="[bold cyan]ℹ️  Info[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )


def create_metadata_table(data):
    """Create metadata display with account information"""
    metadata_lines = [
        f"[dim cyan]🆔 ID:[/dim cyan] {data.get('id', 'N/A')}",
        f"[dim cyan]👤 Type:[/dim cyan] {data.get('type', 'User')}",
        f"[dim cyan]📅 Joined:[/dim cyan] {parse_date(data.get('created_at'))}",
        f"[dim cyan]🔄 Updated:[/dim cyan] {parse_date(data.get('updated_at'))}"
    ]

    return Panel(
        "\n".join(metadata_lines),
        title="[bold yellow]📋 Metadata[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )


def create_stats_panel(data):
    """Create statistics panel with user metrics"""
    stats_lines = [
        f"[dim cyan]📦 Repos:[/dim cyan] {format_number(data.get('public_repos', 0))}",
        f"[dim cyan]👥 Followers:[/dim cyan] {format_number(data.get('followers', 0))}",
        f"[dim cyan]➕ Following:[/dim cyan] {format_number(data.get('following', 0))}",
        f"[dim cyan]📝 Gists:[/dim cyan] {format_number(data.get('public_gists', 0))}"
    ]

    return Panel(
        "\n".join(stats_lines),
        title="[bold bright_magenta]📊 Stats[/bold bright_magenta]",
        border_style="bright_magenta",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )


def create_repos_table(repos):
    """Create a compact repositories table showing top repositories"""
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

    # Sort by stars and limit to top 10
    sorted_repos = sorted(
        repos,
        key=lambda r: r.get('stargazers_count', 0),
        reverse=True
    )[:10]

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


def create_repo_summary(repos):
    """Create a summary panel with repository statistics"""
    total_repos = len(repos)
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
    total_forks = sum(repo.get('forks_count', 0) for repo in repos)

    # Count languages
    languages = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    # Get top 5 languages
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    lang_text = ", ".join([
        f"{LANGUAGE_ICONS.get(lang, '📦')} {lang} ({count})"
        for lang, count in top_languages
    ])

    summary_text = Text()
    summary_text.append(f"📦 Total: {total_repos} repos\n", style="bold cyan")
    summary_text.append(f"⭐ Stars: {format_number(total_stars)}\n", style="bold yellow")
    summary_text.append(f"🍴 Forks: {format_number(total_forks)}\n", style="bold green")
    if top_languages:
        summary_text.append(f"\n🔤 Top Languages:\n{lang_text}", style="dim white")

    return Panel(
        summary_text,
        title="[bold bright_cyan]📊 Repository Summary[/bold bright_cyan]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )


def create_repo_card(repo):
    """Create a detailed card for a single repository"""
    name = repo.get('name', 'N/A')
    description = repo.get('description', 'Aucune description')
    language = repo.get('language', 'Non spécifié')
    stars = format_number(repo.get('stargazers_count', 0))
    forks = format_number(repo.get('forks_count', 0))
    issues = format_number(repo.get('open_issues_count', 0))
    updated = parse_date(repo.get('updated_at'))
    license_info = repo.get('license')
    license_name = license_info.get('name', 'Aucune') if license_info else 'Aucune'
    homepage = repo.get('homepage', '')
    is_fork = repo.get('fork', False)
    default_branch = repo.get('default_branch', 'main')
    html_url = repo.get('html_url', '')
    lang_icon = LANGUAGE_ICONS.get(language, '📦')

    card_text = Text()
    card_text.append(f"📦 {name}", style="bold bright_white")
    if is_fork:
        card_text.append(" 🍴", style="dim yellow")
    card_text.append("\n")

    if description and description != 'Aucune description':
        card_text.append(f"{description}\n", style="italic dim white")

    card_text.append(f"\n{lang_icon} {language}  ", style="cyan")
    card_text.append(f"⭐ {stars}  ", style="yellow")
    card_text.append(f"🍴 {forks}  ", style="green")
    card_text.append(f"🐛 {issues}\n", style="red")

    card_text.append(f"🔄 Updated: {updated}\n", style="dim white")
    card_text.append(f"📜 License: {license_name}\n", style="dim white")
    card_text.append(f"🌿 Branch: {default_branch}\n", style="dim white")

    if homepage:
        card_text.append(f"🌐 {homepage}\n", style="blue")
    if html_url:
        card_text.append(f"🔗 {html_url}", style="blue")

    return Panel(
        card_text,
        border_style="bright_magenta",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True
    )


def display_detailed_repos(repos, limit=20):
    """Display detailed repository information with pagination"""
    sorted_repos = sorted(
        repos,
        key=lambda r: r.get('stargazers_count', 0),
        reverse=True
    )
    limited_repos = sorted_repos[:limit]

    # Display summary first
    console.print(create_repo_summary(repos))

    # Display individual repository cards
    for repo in limited_repos:
        console.print(create_repo_card(repo))

    # Show pagination info if there are more repos
    if len(repos) > limit:
        info_text = (
            f"[dim]Affichage de {limit} sur {len(repos)} repositories "
            f"(utilisez --limit pour voir plus)[/dim]"
        )
        console.print(info_text)


def fetch_with_retry(url, max_retries=3, retry_delay=2, timeout=30):
    """
    Fetch URL with retry logic for handling transient failures

    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        timeout: Request timeout in seconds

    Returns:
        Response object if successful, None otherwise
    """
    headers = {
        'User-Agent': 'Guyteub/0.1.3',
        'Accept': 'application/vnd.github.v3+json'
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                console.print(f"[dim yellow]⏳ Request timeout, retrying ({attempt + 1}/{max_retries})...[/dim yellow]")
                time.sleep(retry_delay)
            else:
                raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [502, 503, 504]:
                if attempt < max_retries - 1:
                    console.print(f"[dim yellow]⏳ Server error (HTTP {e.response.status_code}), retrying ({attempt + 1}/{max_retries})...[/dim yellow]")
                    time.sleep(retry_delay)
                else:
                    raise
            else:
                raise
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                console.print(f"[dim yellow]⏳ Connection error, retrying ({attempt + 1}/{max_retries})...[/dim yellow]")
                time.sleep(retry_delay)
            else:
                raise
    return None


def scrapper(username, show_detailed_repos=False, limit=20):
    """
    Main scraper function that fetches and displays GitHub user information

    Args:
        username: GitHub username to scrape
        show_detailed_repos: Whether to show detailed repository view
        limit: Maximum number of repositories to display
    """
    user_url = f"https://api.github.com/users/{username}"

    try:
        response = fetch_with_retry(user_url)
        if not response:
            raise requests.exceptions.RequestException("Failed to fetch data after retries")
    except requests.exceptions.RequestException as e:
        error_panel = Panel(
            f"[bold red]❌ Request Failed[/bold red]\n\n"
            f"Unable to fetch data for user '[cyan]{username}[/cyan]'\n\n"
            f"Error: {str(e)}\n\n"
            f"[dim]Please verify the username and your internet connection.[/dim]",
            title="[bold red]⚠️  Error[/bold red]",
            border_style="red",
            box=box.HEAVY,
            padding=(0, 1)
        )
        console.print(error_panel)
        return

    data = response.json()

    # Fetch repositories
    repos_url = f"https://api.github.com/users/{username}/repos"
    try:
        repos_response = fetch_with_retry(repos_url)
        repos = repos_response.json() if repos_response else []
    except requests.exceptions.RequestException:
        repos = []

    if show_detailed_repos:
        # Show detailed repository view
        if repos:
            display_detailed_repos(repos, limit=limit)
        else:
            console.print("[dim]Aucun repository trouvé.[/dim]")
    else:
        # Show normal profile view
        header = create_profile_header(data)
        info_section = create_info_section(data)
        metadata_section = create_metadata_table(data)
        stats_panel = create_stats_panel(data)

        # Create container for the three panels
        container = Table.grid(expand=True, padding=(0, 1))
        container.add_column(ratio=1)
        container.add_column(ratio=1)
        container.add_column(ratio=1)
        container.add_row(info_section, metadata_section, stats_panel)

        # Print profile information
        console.print(header)
        console.print(container)

        # Print repositories table if available
        if repos:
            console.print(create_repos_table(repos))
