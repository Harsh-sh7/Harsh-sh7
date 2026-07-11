import os
import requests
import json
from datetime import datetime

class GitHubStatsFetcher:
    def __init__(self, username: str, token: str = None):
        self.username = username
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("PERSONAL_ACCESS_TOKEN")
        self.headers = {"User-Agent": "GitHub-Stats-Fetcher-Agent"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def fetch_all_stats(self) -> dict:
        """
        Orchestrates fetching of all statistics.
        First tries GraphQL API, falls back to REST API if GraphQL fails or has no token.
        Always fetches public events for recent activity.
        """
        stats = {
            "name": self.username,
            "followers": 0,
            "following": 0,
            "public_repos": 0,
            "total_stars": 0,
            "contributions": 0,
            "longest_streak": 0,
            "top_languages": [],
            "pinned_repos": [],
            "latest_repo": "N/A",
            "latest_commit_date": "N/A",
            "recent_activity": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        graphql_success = False
        if self.token:
            try:
                graphql_data = self._fetch_graphql()
                if graphql_data and "data" in graphql_data and graphql_data["data"].get("user"):
                    self._parse_graphql_data(graphql_data["data"]["user"], stats)
                    graphql_success = True
            except Exception as e:
                print(f"GraphQL fetch failed: {e}. Falling back to REST API.")

        if not graphql_success:
            self._fetch_rest_fallback(stats)

        # Recent activity from public events is best fetched via REST API
        try:
            self._fetch_recent_activity(stats)
        except Exception as e:
            print(f"Error fetching recent activity: {e}")

        return stats

    def _fetch_graphql(self) -> dict:
        """
        Queries GitHub GraphQL API for profile info, repositories, contributions, and pinned items.
        """
        query = """
        query($username: String!) {
          user(login: $username) {
            name
            login
            followers { totalCount }
            following { totalCount }
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: CREATED_AT, direction: DESC}) {
              totalCount
              nodes {
                name
                stargazerCount
                createdAt
                pushedAt
                languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
                  edges {
                    size
                    node {
                      name
                      color
                    }
                  }
                }
              }
            }
            pinnedItems(first: 4, types: REPOSITORY) {
              nodes {
                ... on Repository {
                  name
                  description
                  stargazerCount
                  primaryLanguage {
                    name
                    color
                  }
                }
              }
            }
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }
        """
        url = "https://api.github.com/graphql"
        variables = {"username": self.username}
        response = requests.post(url, json={"query": query, "variables": variables}, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _parse_graphql_data(self, user_data: dict, stats: dict):
        """
        Parses GraphQL response into stats dictionary.
        """
        stats["name"] = user_data.get("name") or user_data.get("login")
        stats["followers"] = user_data["followers"]["totalCount"]
        stats["following"] = user_data["following"]["totalCount"]
        
        repos = user_data["repositories"]["nodes"]
        stats["public_repos"] = user_data["repositories"]["totalCount"]
        
        # Calculate total stars and language distribution
        total_stars = 0
        lang_sizes = {}
        lang_colors = {}
        
        latest_pushed = None
        latest_repo_name = "N/A"
        
        for repo in repos:
            total_stars += repo["stargazerCount"]
            
            # Find latest repository by pushed time
            pushed_at_str = repo.get("pushedAt")
            if pushed_at_str:
                pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ")
                if latest_pushed is None or pushed_at > latest_pushed:
                    latest_pushed = pushed_at
                    latest_repo_name = repo["name"]
            
            # Languages
            if "languages" in repo and "edges" in repo["languages"]:
                for edge in repo["languages"]["edges"]:
                    lang_name = edge["node"]["name"]
                    lang_color = edge["node"]["color"] or "#858585"
                    size = edge["size"]
                    lang_sizes[lang_name] = lang_sizes.get(lang_name, 0) + size
                    lang_colors[lang_name] = lang_color
                    
        stats["total_stars"] = total_stars
        stats["latest_repo"] = latest_repo_name
        
        # Format Top Languages
        total_lang_size = sum(lang_sizes.values())
        if total_lang_size > 0:
            sorted_langs = sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)
            # Take top 4 languages
            for lang, size in sorted_langs[:4]:
                pct = (size / total_lang_size) * 100
                stats["top_languages"].append({
                    "name": lang,
                    "percentage": round(pct, 1),
                    "color": lang_colors.get(lang, "#858585")
                })
                
        # Parse Pinned Repos
        pinned_nodes = user_data["pinnedItems"]["nodes"]
        for node in pinned_nodes:
            if node:
                stats["pinned_repos"].append({
                    "name": node["name"],
                    "description": node.get("description") or "No description",
                    "stars": node["stargazerCount"],
                    "language": node["primaryLanguage"]["name"] if node.get("primaryLanguage") else "Text",
                    "language_color": node["primaryLanguage"]["color"] if node.get("primaryLanguage") else "#858585"
                })
                
        # Parse Contributions and Streak
        calendar = user_data["contributionsCollection"]["contributionCalendar"]
        stats["contributions"] = calendar["totalContributions"]
        
        # Calculate streak
        all_days = []
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                all_days.append((day["date"], day["contributionCount"]))
                
        # Sort by date
        all_days.sort(key=lambda x: x[0])
        
        longest_streak = 0
        current_streak = 0
        for date, count in all_days:
            if count > 0:
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
            else:
                current_streak = 0
                
        stats["longest_streak"] = longest_streak

    def _fetch_rest_fallback(self, stats: dict):
        """
        Queries GitHub REST API endpoints as fallback.
        """
        print("Using REST fallback...")
        # 1. Fetch User Profile Info
        profile_url = f"https://api.github.com/users/{self.username}"
        try:
            res = requests.get(profile_url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                stats["name"] = data.get("name") or data.get("login")
                stats["followers"] = data.get("followers", 0)
                stats["following"] = data.get("following", 0)
                stats["public_repos"] = data.get("public_repos", 0)
        except Exception as e:
            print(f"Error fetching REST profile: {e}")

        # 2. Fetch User Repos (up to 100)
        repos_url = f"https://api.github.com/users/{self.username}/repos?per_page=100&sort=created"
        try:
            res = requests.get(repos_url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                repos = res.json()
                total_stars = 0
                lang_sizes = {}
                
                # Filter for non-forks owned by the user
                owned_repos = [r for r in repos if not r.get("fork")]
                
                if owned_repos:
                    # Latest repository is the first in created sort
                    stats["latest_repo"] = owned_repos[0]["name"]
                    
                    for r in owned_repos:
                        total_stars += r.get("stargazers_count", 0)
                        lang = r.get("language")
                        if lang:
                            lang_sizes[lang] = lang_sizes.get(lang, 0) + 1
                            
                    stats["total_stars"] = total_stars
                    
                    # Language percentage fallback (based on count of repos)
                    total_count = sum(lang_sizes.values())
                    if total_count > 0:
                        sorted_langs = sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)
                        for lang, count in sorted_langs[:4]:
                            pct = (count / total_count) * 100
                            stats["top_languages"].append({
                                "name": lang,
                                "percentage": round(pct, 1),
                                "color": "#38bdf8"  # Default blue
                            })
                            
                    # Mock Pinned Repos from highest starred repos
                    sorted_by_stars = sorted(owned_repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
                    for r in sorted_by_stars[:4]:
                        stats["pinned_repos"].append({
                            "name": r["name"],
                            "description": r.get("description") or "No description",
                            "stars": r.get("stargazers_count", 0),
                            "language": r.get("language") or "Text",
                            "language_color": "#38bdf8"
                        })
        except Exception as e:
            print(f"Error fetching REST repos: {e}")

        # Contributions/Streaks fallback to 0 or estimates since REST profile doesn't include it
        stats["contributions"] = 0
        stats["longest_streak"] = 0

    def _fetch_recent_activity(self, stats: dict):
        """
        Fetches public events list and parses the recent activity messages.
        """
        url = f"https://api.github.com/users/{self.username}/events/public?per_page=15"
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code != 200:
            return

        events = res.json()
        activity = []
        latest_commit_date = None

        for event in events:
            ev_type = event.get("type")
            repo_name = event.get("repo", {}).get("name", "")
            
            # Clean up username from repo name (e.g. "Harsh-sh7/my-repo" -> "my-repo")
            if repo_name.startswith(f"{self.username}/"):
                repo_display = repo_name.replace(f"{self.username}/", "")
            else:
                repo_display = repo_name

            created_at_str = event.get("created_at")
            if created_at_str:
                dt = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
                date_str = dt.strftime("%b %d, %Y")
                if latest_commit_date is None and ev_type == "PushEvent":
                    latest_commit_date = date_str

            payload = event.get("payload", {})
            if ev_type == "PushEvent":
                commits = payload.get("commits", [])
                if commits:
                    msg = commits[0].get("message", "").split("\n")[0]
                    if len(msg) > 35:
                        msg = msg[:32] + "..."
                    activity.append(f"Pushed to {repo_display}: '{msg}'")
            elif ev_type == "CreateEvent":
                ref_type = payload.get("ref_type")
                ref = payload.get("ref")
                if ref_type == "repository":
                    activity.append(f"Created repository {repo_display}")
                elif ref_type == "branch":
                    activity.append(f"Created branch {ref} in {repo_display}")
            elif ev_type == "PullRequestEvent":
                action = payload.get("action", "")
                pr = payload.get("pull_request", {})
                number = pr.get("number") or payload.get("number", "N/A")
                activity.append(f"{action.capitalize()} PR #{number} in {repo_display}")
            elif ev_type == "IssuesEvent":
                action = payload.get("action", "")
                issue = payload.get("issue", {})
                number = issue.get("number") or payload.get("number", "N/A")
                activity.append(f"{action.capitalize()} issue #{number} in {repo_display}")
            elif ev_type == "IssueCommentEvent":
                issue = payload.get("issue", {})
                number = issue.get("number") or "N/A"
                activity.append(f"Commented on issue #{number} in {repo_display}")
            elif ev_type == "WatchEvent":
                activity.append(f"Starred repository {repo_display}")

            # Keep only unique and max 3 activities
            unique_activity = []
            for act in activity:
                if act not in unique_activity:
                    unique_activity.append(act)
            if len(unique_activity) >= 3:
                activity = unique_activity[:3]
                break
        
        stats["recent_activity"] = activity if activity else ["No recent public activity"]
        stats["latest_commit_date"] = latest_commit_date or "N/A"



if __name__ == "__main__":
    import sys
    username = "Harsh-sh7"
    if len(sys.argv) > 1:
        username = sys.argv[1]
        
    fetcher = GitHubStatsFetcher(username)
    stats = fetcher.fetch_all_stats()
    print(json.dumps(stats, indent=2))
