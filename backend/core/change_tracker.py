"""
Change Tracker - Tracks configuration changes using local Git

Reads git history from local repository to track when configs were changed.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("⚠️  GitPython not installed. Change tracking will be limited.")
    print("   Install with: pip install gitpython")


class ChangeTracker:
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize change tracker with git repository path.

        Args:
            repo_path: Path to git repository (default: from env var)
        """
        self.repo_path = repo_path or os.getenv('GIT_REPO_PATH', '/path/to/configs')
        self.repo = None

        if GIT_AVAILABLE:
            try:
                self.repo = git.Repo(self.repo_path)
                print(f"✅ Connected to git repo: {self.repo_path}")
            except Exception as e:
                print(f"⚠️  Could not connect to git repo: {e}")
                self.repo = None
        else:
            print("⚠️  Git functionality not available")

    def is_available(self) -> bool:
        """Check if git tracking is available"""
        return self.repo is not None

    def get_changes_since(self, since_date: str, file_pattern: str = "env-*.yaml") -> List[Dict[str, Any]]:
        """
        Get all changes to YAML files since a specific date.

        Args:
            since_date: ISO format date string (e.g., "2024-01-15")
            file_pattern: File pattern to track (default: env-*.yaml)

        Returns:
            List of change records
        """
        if not self.is_available():
            return [{
                'error': 'Git not available',
                'message': 'Change tracking requires git repository'
            }]

        try:
            # Get commits since date
            commits = list(self.repo.iter_commits(
                all=True,
                since=since_date,
                paths=file_pattern
            ))

            changes = []
            for commit in commits:
                # Get files changed in this commit
                for filepath in commit.stats.files.keys():
                    if filepath.endswith(('.yaml', '.yml')):
                        changes.append({
                            'timestamp': commit.committed_datetime.isoformat(),
                            'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            'file': filepath,
                            'environment': self._extract_env_name(filepath),
                            'author': commit.author.email,
                            'author_name': commit.author.name,
                            'message': commit.message.strip(),
                            'commit_hash': commit.hexsha[:7],
                            'stats': commit.stats.files[filepath]
                        })

            # Sort by timestamp (newest first)
            changes.sort(key=lambda x: x['timestamp'], reverse=True)

            return changes

        except Exception as e:
            return [{
                'error': f'Error getting changes: {str(e)}'
            }]

    def get_file_history(self, filename: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get commit history for a specific file.

        Args:
            filename: Name of the file
            limit: Maximum number of commits to return

        Returns:
            List of commits affecting the file
        """
        if not self.is_available():
            return []

        try:
            commits = list(self.repo.iter_commits(
                paths=filename,
                max_count=limit
            ))

            history = []
            for commit in commits:
                history.append({
                    'timestamp': commit.committed_datetime.isoformat(),
                    'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'author': commit.author.email,
                    'author_name': commit.author.name,
                    'message': commit.message.strip(),
                    'commit_hash': commit.hexsha[:7],
                    'full_hash': commit.hexsha
                })

            return history

        except Exception as e:
            print(f"Error getting file history: {e}")
            return []

    def get_file_diff(self, filename: str, commit_hash: str = 'HEAD') -> Optional[str]:
        """
        Get diff for a specific file at a commit.

        Args:
            filename: Name of the file
            commit_hash: Commit hash (default: HEAD)

        Returns:
            Diff string or None
        """
        if not self.is_available():
            return None

        try:
            commit = self.repo.commit(commit_hash)
            if not commit.parents:
                return "Initial commit (no diff available)"

            parent = commit.parents[0]
            diffs = parent.diff(commit, paths=filename, create_patch=True)

            if diffs:
                return diffs[0].diff.decode('utf-8')
            return "No changes"

        except Exception as e:
            print(f"Error getting diff: {e}")
            return None

    def get_last_modified(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get last modification info for a file.

        Args:
            filename: Name of the file

        Returns:
            Last modification info or None
        """
        if not self.is_available():
            # Fallback to filesystem modification time
            try:
                file_path = Path(self.repo_path) / filename
                if file_path.exists():
                    mtime = file_path.stat().st_mtime
                    dt = datetime.fromtimestamp(mtime)
                    return {
                        'timestamp': dt.isoformat(),
                        'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'filesystem'
                    }
            except:
                pass
            return None

        try:
            commits = list(self.repo.iter_commits(paths=filename, max_count=1))
            if not commits:
                return None

            commit = commits[0]
            return {
                'timestamp': commit.committed_datetime.isoformat(),
                'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'author': commit.author.email,
                'author_name': commit.author.name,
                'message': commit.message.strip(),
                'commit_hash': commit.hexsha[:7],
                'source': 'git'
            }

        except Exception as e:
            print(f"Error getting last modified: {e}")
            return None

    def get_recent_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent activity across all config files.

        Args:
            days: Number of days to look back

        Returns:
            List of recent changes
        """
        if not self.is_available():
            return []

        since_date = datetime.now()
        since_date = since_date.replace(day=since_date.day - days)
        since_str = since_date.strftime('%Y-%m-%d')

        return self.get_changes_since(since_str)

    def get_changes_between(self, env1: str, env2: str) -> Dict[str, Any]:
        """
        Compare changes between two environment files over time.

        Args:
            env1: First environment name
            env2: Second environment name

        Returns:
            Comparison of changes
        """
        if not self.is_available():
            return {'error': 'Git not available'}

        file1 = f"env-{env1}.yaml"
        file2 = f"env-{env2}.yaml"

        history1 = self.get_file_history(file1, limit=5)
        history2 = self.get_file_history(file2, limit=5)

        return {
            'environment1': env1,
            'environment2': env2,
            'history1': history1,
            'history2': history2,
            'recent_changes1': len(history1),
            'recent_changes2': len(history2)
        }

    def _extract_env_name(self, filepath: str) -> str:
        """
        Extract environment name from file path.

        Args:
            filepath: File path

        Returns:
            Environment name
        """
        filename = Path(filepath).name
        # Remove env- prefix and .yaml/.yml suffix
        name = filename.replace('env-', '').replace('.yaml', '').replace('.yml', '')
        return name

    def get_status(self) -> Dict[str, Any]:
        """
        Get git repository status.

        Returns:
            Status information
        """
        if not self.is_available():
            return {
                'available': False,
                'message': 'Git tracking not available'
            }

        try:
            return {
                'available': True,
                'repo_path': self.repo_path,
                'current_branch': self.repo.active_branch.name,
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': len(self.repo.untracked_files),
                'total_commits': len(list(self.repo.iter_commits()))
            }
        except Exception as e:
            return {
                'available': True,
                'error': str(e)
            }
