"""
GitHub Activity API Fetcher
Handles fetching event data from GitHub API
"""
import requests
import time
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
        self.headers = {
            'User-Agent': 'Guyteub/0.1.3',
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'

    def _fetch_with_retry(self, url: str, params: Dict = None, max_retries: int = 3, retry_delay: int = 2) -> requests.Response:
        """
        Fetch URL with retry logic for handling transient failures

        Args:
            url: URL to fetch
            params: Request parameters
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Response object if successful

        Raises:
            requests.RequestException: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Request timeout, retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                else:
                    raise
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [502, 503, 504]:
                    if attempt < max_retries - 1:
                        print(f"Server error (HTTP {e.response.status_code}), retrying ({attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
                    else:
                        raise
                else:
                    raise
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    print(f"Connection error, retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                else:
                    raise
        raise requests.exceptions.RequestException("Failed to fetch data after retries")

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
                response = self._fetch_with_retry(
                    f"{self.BASE_URL}/users/{username}/events",
                    params={"page": page, "per_page": 30}
                )
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
                response = self._fetch_with_retry(
                    f"{self.BASE_URL}/users/{username}/events/public",
                    params={"page": page, "per_page": 30}
                )
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
