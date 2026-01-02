"""
GitHub Activity API Fetcher
Handles fetching event data from GitHub API
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class GitHubActivityAPI:
    """Fetch GitHub activity/events from API"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize with optional GitHub token for higher rate limits

        Args:
            token: Optional GitHub personal access token
        """
        self.token = token
        self.headers = {}
        if token:
            self.headers['Authorization'] = f'token {token}'

    def fetch_user_events(
        self,
        username: str,
        max_pages: int = 10,
        days_limit: int = 90
    ) -> List[Dict]:
        """
        Fetch user events from GitHub API

        Args:
            username: GitHub username
            max_pages: Maximum number of pages to fetch (30 events per page)
            days_limit: Only include events within this many days

        Returns:
            List of event dictionaries

        Raises:
            requests.HTTPError: If API request fails
        """
        all_events = []
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_limit)

        for page in range(1, max_pages + 1):
            try:
                response = requests.get(
                    f"{self.BASE_URL}/users/{username}/events",
                    headers=self.headers,
                    params={"page": page, "per_page": 30},
                    timeout=10
                )
                response.raise_for_status()
                events = response.json()

                if not events:
                    # No more events
                    break

                # Filter by date
                for event in events:
                    event_date = datetime.fromisoformat(
                        event['created_at'].replace('Z', '+00:00')
                    )
                    if event_date >= cutoff_date:
                        all_events.append(event)
                    else:
                        # Events are sorted by date, so we can stop
                        return all_events

            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération des événements (page {page}): {e}")
                break

        return all_events

    def fetch_public_events(
        self,
        username: str,
        max_pages: int = 10
    ) -> List[Dict]:
        """
        Fetch only public events (alternative endpoint)

        Args:
            username: GitHub username
            max_pages: Maximum number of pages to fetch

        Returns:
            List of public event dictionaries
        """
        all_events = []

        for page in range(1, max_pages + 1):
            try:
                response = requests.get(
                    f"{self.BASE_URL}/users/{username}/events/public",
                    headers=self.headers,
                    params={"page": page, "per_page": 30},
                    timeout=10
                )
                response.raise_for_status()
                events = response.json()

                if not events:
                    break

                all_events.extend(events)

            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération des événements publics: {e}")
                break

        return all_events

    def get_rate_limit_info(self) -> Dict:
        """
        Get current rate limit information

        Returns:
            Dictionary with rate limit details
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/rate_limit",
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def check_user_exists(self, username: str) -> bool:
        """
        Check if a GitHub user exists

        Args:
            username: GitHub username to check

        Returns:
            True if user exists, False otherwise
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/users/{username}",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
