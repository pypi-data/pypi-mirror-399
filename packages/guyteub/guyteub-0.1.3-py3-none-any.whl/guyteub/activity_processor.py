"""
GitHub Activity Data Processor
Processes event data and prepares it for visualization
"""
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import requests


class ActivityProcessor:
    """Process GitHub events data for visualization"""

    EVENT_ICONS = {
        'PushEvent': '🚀',
        'PullRequestEvent': '🔀',
        'WatchEvent': '⭐',
        'ForkEvent': '🍴',
        'IssueCommentEvent': '💬',
        'IssuesEvent': '🐛',
        'CreateEvent': '✨',
        'DeleteEvent': '🗑️',
        'PullRequestReviewEvent': '👀',
        'PullRequestReviewCommentEvent': '💭',
        'ReleaseEvent': '🎉',
        'PublicEvent': '🌍'
    }

    EVENT_COLORS = {
        'PushEvent': 'cyan',
        'PullRequestEvent': 'magenta',
        'WatchEvent': 'yellow',
        'ForkEvent': 'green',
        'IssueCommentEvent': 'blue',
        'IssuesEvent': 'red',
        'CreateEvent': 'bright_green',
        'DeleteEvent': 'bright_black',
        'PullRequestReviewEvent': 'bright_magenta',
        'PullRequestReviewCommentEvent': 'bright_blue',
        'ReleaseEvent': 'bright_yellow',
        'PublicEvent': 'bright_cyan'
    }

    FRENCH_LABELS = {
        'PushEvent': 'Commits',
        'PullRequestEvent': 'Pull Requests',
        'WatchEvent': 'Stars',
        'ForkEvent': 'Forks',
        'IssueCommentEvent': 'Commentaires',
        'IssuesEvent': 'Issues',
        'CreateEvent': 'Créations',
        'DeleteEvent': 'Suppressions',
        'PullRequestReviewEvent': 'Revues',
        'PullRequestReviewCommentEvent': 'Commentaires PR',
        'ReleaseEvent': 'Releases',
        'PublicEvent': 'Rendus publics'
    }

    def __init__(self, events: List[Dict]):
        """Initialize with raw events from GitHub API"""
        self.events = events
        self.daily_counts = self._compute_daily_counts()
        self.event_type_counts = self._compute_event_types()
        self.repo_activity = self._compute_repo_activity()

    def _compute_daily_counts(self) -> Dict[str, int]:
        """Compute number of events per day"""
        daily = defaultdict(int)
        for event in self.events:
            date = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
            day_key = date.strftime('%Y-%m-%d')
            daily[day_key] += 1
        return dict(daily)

    def _compute_event_types(self) -> Counter:
        """Count events by type"""
        return Counter(event['type'] for event in self.events)

    def _compute_repo_activity(self) -> Dict[str, int]:
        """Count events per repository"""
        repo_counts = defaultdict(int)
        for event in self.events:
            repo_name = event.get('repo', {}).get('name', 'Unknown')
            repo_counts[repo_name] += 1
        # Return sorted by count
        return dict(sorted(repo_counts.items(), key=lambda x: x[1], reverse=True))

    def get_heatmap_data(self, days: int = 30) -> List[Tuple[str, int]]:
        """
        Get heatmap data for the last N days
        Returns list of (date_string, count) tuples
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)

        heatmap = []
        current = start_date
        while current <= end_date:
            day_key = current.strftime('%Y-%m-%d')
            count = self.daily_counts.get(day_key, 0)
            heatmap.append((day_key, count))
            current += timedelta(days=1)

        return heatmap

    def get_intensity_color(self, count: int) -> str:
        """Get color based on activity intensity"""
        if count == 0:
            return 'dim'
        elif count <= 3:
            return 'green'
        elif count <= 7:
            return 'cyan'
        elif count <= 12:
            return 'blue'
        else:
            return 'magenta'

    def get_intensity_char(self, count: int) -> str:
        """Get Unicode character based on intensity"""
        if count == 0:
            return '░'
        elif count <= 3:
            return '▒'
        elif count <= 7:
            return '▓'
        else:
            return '█'

    def get_total_contributions(self) -> int:
        """Get total number of events"""
        return len(self.events)

    def get_active_days(self) -> int:
        """Get number of days with at least one event"""
        return len([count for count in self.daily_counts.values() if count > 0])

    def get_current_streak(self) -> int:
        """Calculate current contribution streak"""
        streak = 0
        current_date = datetime.now()

        while True:
            day_key = current_date.strftime('%Y-%m-%d')
            if self.daily_counts.get(day_key, 0) > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return streak

    def get_longest_streak(self) -> int:
        """Calculate longest contribution streak"""
        if not self.daily_counts:
            return 0

        # Get all dates sorted
        dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in self.daily_counts.keys()])

        longest = current = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def get_busiest_day(self) -> Tuple[str, int]:
        """Get the day with most activity"""
        if not self.daily_counts:
            return ("Aucun", 0)

        busiest = max(self.daily_counts.items(), key=lambda x: x[1])
        return busiest

    def get_top_repos(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get top N most active repositories"""
        return list(self.repo_activity.items())[:limit]
