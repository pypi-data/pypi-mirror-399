import requests
from typing import List, Dict
from .client import GitHubClient

class IssueManager:

    def __init__(self, client: GitHubClient):
        self.client = client

    def list_issues(self, repo: str, state: str = 'open') -> List[Dict]:
        url = f"{self.client.base_url}/repos/{repo}/issues?state={state}"
        response = requests.get(url, headers=self.client.headers)
        if response.status_code == 200:
            return response.json()
        return []