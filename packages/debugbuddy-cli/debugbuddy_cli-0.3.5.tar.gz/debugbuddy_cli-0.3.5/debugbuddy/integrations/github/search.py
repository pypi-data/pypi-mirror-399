from typing import List, Dict
from .client import GitHubClient

class GitHubSearcher:

    def __init__(self, client: GitHubClient):
        self.client = client

    def find_solutions(self, error_type: str, language: str, 
                      limit: int = 5) -> List[Dict]:
        issues = self.client.search_issues(error_type, language)

        solutions = []
        for issue in issues[:limit]:
            solutions.append({
                'title': issue['title'],
                'url': issue['html_url'],
                'state': issue['state'],
                'reactions': issue.get('reactions', {}).get('total_count', 0),
                'comments': issue.get('comments', 0)
            })

        return solutions