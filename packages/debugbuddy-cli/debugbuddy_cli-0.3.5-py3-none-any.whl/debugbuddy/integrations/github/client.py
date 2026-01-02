import requests
from typing import List, Dict, Optional

class GitHubClient:

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def search_issues(self, error_type: str, language: str) -> List[Dict]:
        query = f"{error_type} language:{language}"
        url = f"{self.base_url}/search/issues?q={query}&sort=reactions"

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []

    def create_issue(self, repo: str, title: str, body: str, 
                    labels: List[str] = None) -> Dict:
        url = f"{self.base_url}/repos/{repo}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": labels or []
        }

        response = requests.post(url, json=data, headers=self.headers)
        return response.json()