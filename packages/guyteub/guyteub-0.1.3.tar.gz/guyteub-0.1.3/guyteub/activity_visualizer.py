"""
GitHub Activity Visualizer using Rich library
Creates beautiful terminal-based activity visualizations
"""
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box
from datetime import datetime, timedelta
from typing import List, Tuple
from .activity_processor import ActivityProcessor


class ActivityVisualizer:
    """Create Rich-based visualizations for GitHub activity"""

    def __init__(self, processor: ActivityProcessor, username: str):
        self.processor = processor
        self.username = username
        self.console = Console()

    def create_annual_github_calendar(self, days: int = 365) -> Panel:
        """
        GitHub-style horizontal activity calendar - Redesigned for clarity
        Features: Better month separators, improved spacing, visual week grouping
        """
        heatmap_data = self.processor.get_heatmap_data(days)
        lines = []

        start_date = datetime.strptime(heatmap_data[0][0], '%Y-%m-%d')
        end_date = datetime.strptime(heatmap_data[-1][0], '%Y-%m-%d')

        # French month names (shortened)
        french_months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                        'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

        # Build month header with better visual separation
        months_row = Text("       ", style="dim")  # Day label padding
        current_month = start_date.month
        month_positions = {}  # Track where months start for separators

        for week_idx in range(0, len(heatmap_data), 7):
            if week_idx >= len(heatmap_data):
                break
            week_start = datetime.strptime(heatmap_data[week_idx][0], '%Y-%m-%d')

            if week_start.month != current_month:
                month_name = french_months[week_start.month - 1]
                months_row.append(f" {month_name}", style="bold bright_yellow")
                month_positions[week_idx // 7] = True
                current_month = week_start.month
            else:
                months_row.append("    ", style="dim")

        lines.append(months_row)
        lines.append(Text())  # Spacing

        # Build calendar grid - all 7 days for better visualization
        day_names = [
            ('Lun', 0, 'cyan'),
            ('Mar', 1, 'dim cyan'),
            ('Mer', 2, 'cyan'),
            ('Jeu', 3, 'dim cyan'),
            ('Ven', 4, 'cyan'),
            ('Sam', 5, 'bright_magenta'),
            ('Dim', 6, 'bright_magenta')
        ]

        for day_name, day_offset, day_color in day_names:
            row = Text(f"  {day_name}  ", style=day_color)

            # Get the first occurrence of this day
            first_day = start_date
            while first_day.weekday() != day_offset:
                first_day += timedelta(days=1)

            current_date = first_day
            week_count = 0

            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                count = self.processor.daily_counts.get(date_str, 0)

                # Get character and color based on intensity
                char = self._get_enhanced_char(count)
                color = self._get_enhanced_color(count)

                # Add visual separator between months
                if week_count in month_positions and week_count > 0:
                    row.append(" ", style="dim")

                row.append(char, style=color)
                current_date += timedelta(days=7)
                week_count += 1

            lines.append(row)

        # Enhanced legend and statistics
        lines.append(Text())

        # Legend with better spacing
        legend = Text("       ", style="dim")
        legend.append("Activité:  ", style="bold dim")
        legend.append("░", style="dim white")
        legend.append(" Aucune   ", style="dim")
        legend.append("▒", style="green")
        legend.append(" Faible   ", style="dim")
        legend.append("▓", style="bright_green")
        legend.append(" Moyenne   ", style="dim")
        legend.append("█", style="cyan")
        legend.append(" Élevée   ", style="dim")
        legend.append("█", style="bold magenta")
        legend.append(" Très élevée", style="dim")
        lines.append(legend)

        # Statistics with visual separation
        lines.append(Text())
        total_events = self.processor.get_total_contributions()
        longest_streak = self.processor.get_longest_streak()
        current_streak = self.processor.get_current_streak()
        active_days = self.processor.get_active_days()

        stats = Text("       ", style="dim")
        stats.append("📊 ", style="bright_cyan")
        stats.append(f"{total_events}", style="bold bright_cyan")
        stats.append(" contributions", style="dim")
        stats.append("  •  ", style="dim")
        stats.append("🔥 ", style="bright_magenta")
        stats.append(f"{current_streak}", style="bold bright_magenta")
        stats.append(" jours actuels", style="dim")
        stats.append("  •  ", style="dim")
        stats.append("⭐ ", style="bright_yellow")
        stats.append(f"{longest_streak}", style="bold bright_yellow")
        stats.append(" jours max", style="dim")
        stats.append("  •  ", style="dim")
        stats.append("📅 ", style="bright_green")
        stats.append(f"{active_days}", style="bold bright_green")
        stats.append(" jours actifs", style="dim")

        lines.append(stats)

        content = Group(*lines)
        return Panel(
            content,
            title=f"[bold bright_cyan]📅 Calendrier d'activité ({days} derniers jours)[/bold bright_cyan]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )

    def _get_enhanced_char(self, count: int) -> str:
        """Get Unicode character for 5-level intensity scale"""
        if count == 0:
            return "░"
        elif count <= 2:
            return "▒"
        elif count <= 5:
            return "▓"
        elif count <= 9:
            return "█"
        else:
            return "█"

    def _get_enhanced_color(self, count: int) -> str:
        """Get color for 5-level intensity scale (GitHub-inspired)"""
        if count == 0:
            return "dim white"
        elif count <= 2:
            return "green"
        elif count <= 5:
            return "bright_green"
        elif count <= 9:
            return "cyan"
        else:
            return "bold magenta"

    def create_stats_panel(self) -> Panel:
        """
        Create statistics panel with key metrics
        3-column layout
        """
        total_events = self.processor.get_total_contributions()
        active_days = self.processor.get_active_days()
        current_streak = self.processor.get_current_streak()
        longest_streak = self.processor.get_longest_streak()
        busiest_day, busiest_count = self.processor.get_busiest_day()

        # Format busiest day
        if busiest_day != "Aucun":
            date_obj = datetime.strptime(busiest_day, '%Y-%m-%d')
            busiest_formatted = date_obj.strftime('%d/%m/%Y')
        else:
            busiest_formatted = "Aucun"

        # Create 3 sub-panels
        # Column 1: Total stats
        col1 = Text()
        col1.append("📊 Total d'événements\n", style="bold yellow")
        col1.append(f"{total_events}\n\n", style="bold bright_cyan")
        col1.append("📅 Jours actifs\n", style="bold yellow")
        col1.append(f"{active_days} jours", style="bold green")

        # Column 2: Streak info
        col2 = Text()
        col2.append("🔥 Série actuelle\n", style="bold yellow")
        col2.append(f"{current_streak} jours\n\n", style="bold magenta")
        col2.append("⭐ Série maximale\n", style="bold yellow")
        col2.append(f"{longest_streak} jours", style="bold blue")

        # Column 3: Peak activity
        col3 = Text()
        col3.append("📈 Jour le + actif\n", style="bold yellow")
        col3.append(f"{busiest_formatted}\n\n", style="bold cyan")
        col3.append("💪 Contributions\n", style="bold yellow")
        col3.append(f"{busiest_count} événements", style="bold green")

        # Create columns
        columns = Columns([col1, col2, col3], equal=True, expand=True)

        return Panel(
            columns,
            title="📊 Statistiques d'activité",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def create_event_distribution_chart(self) -> Panel:
        """
        Create horizontal bar chart for event type distribution
        Uses Table for perfect alignment regardless of emoji width
        """
        event_counts = self.processor.event_type_counts
        total = sum(event_counts.values())

        if total == 0:
            return Panel(
                Text("Aucune activité détectée", style="dim"),
                title="📈 Répartition par type d'événement",
                border_style="yellow",
                box=box.ROUNDED,
                padding=(0, 1)
            )

        # Create table with fixed-width columns for perfect alignment
        table = Table(
            show_header=False,
            box=None,
            padding=(0, 0),
            collapse_padding=False,
            pad_edge=False
        )

        # Define columns with exact widths
        table.add_column("icon", width=2, justify="left")
        table.add_column("label", width=20, justify="left", no_wrap=True)
        table.add_column("bar", width=30, justify="left", no_wrap=True)
        table.add_column("count", width=4, justify="right")
        table.add_column("percentage", width=9, justify="left")

        # Sort by count
        sorted_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)

        # Take top 8 to avoid clutter
        for event_type, count in sorted_events[:8]:
            icon = self.processor.EVENT_ICONS.get(event_type, '📌')
            color = self.processor.EVENT_COLORS.get(event_type, 'white')
            label = self.processor.FRENCH_LABELS.get(event_type, event_type)

            percentage = (count / total) * 100
            bar_width = 30
            filled = int((count / total) * bar_width)

            # Build bar visualization as separate Text objects
            icon_text = Text(icon, style=color)
            label_text = Text(label, style="white")

            bar_text = Text()
            bar_text.append("█" * filled, style=color)
            bar_text.append("░" * (bar_width - filled), style="dim")

            count_text = Text(f"{count}", style="bold white")
            percentage_text = Text(f"({percentage:5.1f}%)", style="dim")

            table.add_row(
                icon_text,
                label_text,
                bar_text,
                count_text,
                percentage_text
            )

        return Panel(
            table,
            title="📈 Répartition par type d'événement",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 2)
        )

    def create_top_repos_table(self, limit: int = 5) -> Panel:
        """
        Create table showing most active repositories
        """
        top_repos = self.processor.get_top_repos(limit)

        if not top_repos:
            return Panel(
                Text("Aucun dépôt actif", style="dim"),
                title="🏆 Dépôts les plus actifs",
                border_style="magenta",
                box=box.ROUNDED,
                padding=(0, 1)
            )

        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            padding=(0, 1),
            collapse_padding=True
        )

        table.add_column("🏅", style="yellow", width=3, justify="center")
        table.add_column("Dépôt", style="cyan", no_wrap=False)
        table.add_column("Contributions", style="green", justify="right", width=14)
        table.add_column("Part", style="dim", justify="right", width=8)

        total_events = self.processor.get_total_contributions()

        for rank, (repo_name, count) in enumerate(top_repos, 1):
            # Medal emojis for top 3
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"{rank}")
            percentage = (count / total_events * 100) if total_events > 0 else 0

            table.add_row(
                medal,
                repo_name,
                f"{count} événements",
                f"{percentage:.1f}%"
            )

        return Panel(
            table,
            title="🏆 Dépôts les plus actifs",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def create_activity_timeline(self, limit: int = 10) -> Panel:
        """
        Create a timeline of recent events
        Shows the most recent activity in chronological order
        """
        # Get recent events (already sorted by date in API response)
        recent_events = self.processor.events[:limit]

        if not recent_events:
            return Panel(
                Text("Aucune activité récente", style="dim"),
                title="⏱️  Activité récente",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 1)
            )

        lines = []

        for event in recent_events:
            event_type = event['type']
            icon = self.processor.EVENT_ICONS.get(event_type, '📌')
            color = self.processor.EVENT_COLORS.get(event_type, 'white')
            label = self.processor.FRENCH_LABELS.get(event_type, event_type)

            # Parse timestamp
            created_at = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
            time_str = created_at.strftime('%d/%m %H:%M')

            # Get repo name
            repo_name = event.get('repo', {}).get('name', 'Unknown')

            # Create line
            line = Text()
            line.append(f"{time_str} ", style="dim")
            line.append(f"{icon} ", style=color)
            line.append(f"{label:<18}", style=color)
            line.append(f" → {repo_name}", style="bright_black")

            lines.append(line)

        content = Group(*lines)
        return Panel(
            content,
            title="⏱️  Activité récente",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def render_full_activity_view(self) -> None:
        """
        Render only the activity calendar (annual view)
        """
        # Main title
        title = Panel(
            Text(f"📊 Activité GitHub - {self.username}", style="bold bright_cyan", justify="center"),
            border_style="bright_cyan",
            box=box.DOUBLE
        )

        self.console.print(title)
        self.console.print()

        # Annual Calendar (365 days)
        self.console.print(self.create_annual_github_calendar(days=365))

    def render_stats_view(self) -> None:
        """
        Render detailed statistics with top repos and event distribution
        """
        # Main title
        title = Panel(
            Text(f"📊 Statistiques GitHub - {self.username}", style="bold bright_cyan", justify="center"),
            border_style="bright_cyan",
            box=box.DOUBLE
        )

        self.console.print(title)
        self.console.print()

        # Statistics panel
        self.console.print(self.create_stats_panel())
        self.console.print()

        # Event distribution
        self.console.print(self.create_event_distribution_chart())
        self.console.print()

        # Top repositories
        self.console.print(self.create_top_repos_table())
        self.console.print()

        # Recent activity timeline
        self.console.print(self.create_activity_timeline())

    def render_compact_view(self) -> None:
        """
        Render a compact version with just heatmap and stats
        Useful for quick overview or narrow terminals
        """
        title = Panel(
            Text(f"📊 {self.username} - Activité", style="bold cyan", justify="center"),
            border_style="cyan",
            box=box.ROUNDED
        )

        self.console.print(title)
        self.console.print()
        self.console.print(self.create_heatmap_calendar())
        self.console.print()
        self.console.print(self.create_stats_panel())
