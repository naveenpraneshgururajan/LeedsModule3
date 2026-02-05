"""
Multi-Repository YAML Configuration Parser

Handles multiple repositories with different folder structures.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import glob


class MultiRepoParser:
    def __init__(self, repos_config_path: str = "repositories.yaml"):
        """
        Initialize multi-repo parser.

        Args:
            repos_config_path: Path to repositories.yaml configuration
        """
        self.repos_config_path = repos_config_path
        self.repositories = []
        self.load_repositories_config()

    def load_repositories_config(self):
        """Load repositories configuration from YAML"""
        config_path = Path(self.repos_config_path)

        if not config_path.exists():
            print(f"⚠️  Repositories config not found: {self.repos_config_path}")
            print("   Using fallback to single repo mode")
            return

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.repositories = config.get('repositories', [])
                self.env_extraction = config.get('environment_extraction', {})
                print(f"✅ Loaded {len(self.repositories)} repositories from config")
        except Exception as e:
            print(f"❌ Error loading repositories config: {e}")

    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def load_yaml_file(self, file_path: Path) -> Optional[Dict]:
        """Load a single YAML file"""
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
                return content if content else {}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def get_environments_from_simple_repo(self, repo: Dict) -> List[Dict[str, Any]]:
        """
        Get environments from simple structure repository.
        Structure: env-dev01.yaml, env-cit01.yaml (files in root)
        """
        environments = []
        repo_path = Path(repo['path'])

        if not repo_path.exists():
            print(f"⚠️  Repository path not found: {repo['path']}")
            return []

        file_pattern = repo.get('file_pattern', '*.yaml')

        for file_path in repo_path.glob(file_pattern):
            if not file_path.is_file():
                continue

            # Extract environment name from filename
            env_name = self.extract_env_name_from_filename(file_path.name, repo)

            # Load YAML content
            content = self.load_yaml_file(file_path)

            if content:
                flattened = self.flatten_dict(content)

                # Categorize the file
                category = self.categorize_file(file_path)
                categorized_configs = {
                    'switches': {},
                    'configmap': {},
                    'cwa': {},
                    'node': {},
                    'dsapps': {},
                    'other': {}
                }
                categorized_configs[category][file_path.stem] = content

                env_data = {
                    'name': env_name,
                    'repository': repo['name'],
                    'filename': file_path.name,
                    'full_path': str(file_path),
                    'type': self.get_environment_type(env_name),
                    'structure': 'simple',
                    'total_keys': len(flattened),
                    'config': content,
                    'flattened_config': flattened,
                    'files': [str(file_path)],  # Single file
                    'categorized_configs': categorized_configs,  # NEW: Configs by category
                    'file_categories': {file_path.stem: category}  # NEW: File to category mapping
                }
                environments.append(env_data)

        return environments

    def categorize_file(self, file_path: Path) -> str:
        """
        Categorize file based on its name or location.

        Returns:
            Category name: 'switches', 'configmap', 'cwa', 'node', or 'other'
        """
        filename = file_path.name.lower()
        stem = file_path.stem.lower()

        # Check if it's in a cwa folder or matches cwa pattern
        if 'cwa' in str(file_path).lower():
            return 'cwa'

        # Check for feature switches
        if 'switch' in stem or stem == 'feature-switches':
            return 'switches'

        # Check for config map or adgroup
        if 'configmap' in stem or 'config-map' in stem or 'adgroup' in stem:
            return 'configmap'

        # Check for node yaml
        if 'node' in stem:
            return 'node'

        # Check for dsapps
        if 'dsapp' in str(file_path).lower():
            return 'dsapps'

        return 'other'

    def get_environments_from_folder_repo(self, repo: Dict) -> List[Dict[str, Any]]:
        """
        Get environments from folder structure repository.
        Structure: src/env/cit01/feature-switches.yaml, src/env/cit01/adgroup.yaml, etc.
        """
        environments = []
        repo_path = Path(repo['path'])
        base_path = repo.get('base_path', '')

        if not repo_path.exists():
            print(f"⚠️  Repository path not found: {repo['path']}")
            return []

        # Get environment folders
        env_base = repo_path / base_path
        if not env_base.exists():
            print(f"⚠️  Environment base path not found: {env_base}")
            return []

        # Iterate through environment folders
        for env_folder in env_base.iterdir():
            if not env_folder.is_dir():
                continue

            env_name = env_folder.name

            # Aggregate all YAML files in this environment
            aggregated_config = {}
            yaml_files = []
            file_patterns = repo.get('file_patterns', ['*.yaml'])

            # Categorized configs for better UI display
            categorized_configs = {
                'switches': {},
                'configmap': {},
                'cwa': {},
                'node': {},
                'dsapps': {},
                'other': {}
            }

            file_categories = {}

            for pattern in file_patterns:
                # Find all matching files
                for file_path in env_folder.glob(pattern):
                    if file_path.is_file():
                        yaml_files.append(str(file_path))
                        content = self.load_yaml_file(file_path)

                        if content:
                            # Categorize this file
                            category = self.categorize_file(file_path)
                            file_prefix = file_path.stem  # e.g., "feature-switches"
                            file_categories[file_prefix] = category

                            # Store in categorized config
                            if file_prefix not in categorized_configs[category]:
                                categorized_configs[category][file_prefix] = content

                            # Prefix keys with filename for uniqueness in aggregated config
                            for key, value in content.items():
                                prefixed_key = f"{file_prefix}.{key}"
                                aggregated_config[prefixed_key] = value

            if aggregated_config:
                flattened = self.flatten_dict(aggregated_config)

                env_data = {
                    'name': env_name,
                    'repository': repo['name'],
                    'folder': env_folder.name,
                    'full_path': str(env_folder),
                    'type': self.get_environment_type(env_name),
                    'structure': 'folder',
                    'total_keys': len(flattened),
                    'config': aggregated_config,
                    'flattened_config': flattened,
                    'files': yaml_files,  # Multiple files
                    'categorized_configs': categorized_configs,  # NEW: Configs by category
                    'file_categories': file_categories  # NEW: File to category mapping
                }
                environments.append(env_data)

        return environments

    def get_all_environments(self) -> List[Dict[str, Any]]:
        """
        Get all environments from all enabled repositories.

        Returns:
            List of environment dictionaries from all repos
        """
        all_environments = []

        for repo in self.repositories:
            if not repo.get('enabled', True):
                continue

            print(f"\n📂 Processing repository: {repo['name']}")

            structure = repo.get('structure', 'simple')

            if structure == 'simple':
                envs = self.get_environments_from_simple_repo(repo)
            elif structure == 'folder':
                envs = self.get_environments_from_folder_repo(repo)
            else:
                print(f"⚠️  Unknown structure type: {structure}")
                continue

            print(f"   Found {len(envs)} environments")
            all_environments.extend(envs)

        print(f"\n✅ Total environments across all repos: {len(all_environments)}")
        return all_environments

    def get_environment(self, env_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific environment by name (searches all repos).

        Args:
            env_name: Environment name

        Returns:
            Environment data or None
        """
        all_envs = self.get_all_environments()

        for env in all_envs:
            if env['name'] == env_name:
                return env

        return None

    def get_environments_by_repo(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all environments from a specific repository"""
        all_envs = self.get_all_environments()
        return [env for env in all_envs if env['repository'] == repo_name]

    def extract_env_name_from_filename(self, filename: str, repo: Dict) -> str:
        """
        Extract environment name from filename.
        e.g., "env-dev01.yaml" -> "dev01"
        """
        # Remove extension
        name = filename.replace('.yaml', '').replace('.yml', '')

        # Try to extract using pattern
        pattern = self.env_extraction.get('file_pattern', 'env-{env_name}.yaml')

        if '{env_name}' in pattern:
            prefix = pattern.split('{env_name}')[0]
            if name.startswith(prefix):
                name = name[len(prefix):]

        return name

    def get_environment_type(self, env_name: str) -> str:
        """Determine environment type from name"""
        name_lower = env_name.lower()

        if name_lower.startswith('dev'):
            return 'dev'
        elif name_lower.startswith('cit'):
            return 'cit'
        elif name_lower.startswith('sit'):
            return 'sit'
        elif name_lower.startswith('luat'):
            return 'luat'
        elif name_lower.startswith('desktop') or name_lower.startswith('prod'):
            return 'prod'
        else:
            return 'unknown'

    def get_all_unique_keys(self) -> List[str]:
        """Get all unique keys across all environments and repos"""
        all_keys = set()
        environments = self.get_all_environments()

        for env in environments:
            all_keys.update(env['flattened_config'].keys())

        return sorted(list(all_keys))

    def compare(self, source_env: str, target_env: str) -> Dict[str, Any]:
        """Compare two environments (can be from different repos)"""
        source = self.get_environment(source_env)
        target = self.get_environment(target_env)

        if not source or not target:
            return {
                'error': 'One or both environments not found',
                'source_found': source is not None,
                'target_found': target is not None
            }

        source_keys = set(source['flattened_config'].keys())
        target_keys = set(target['flattened_config'].keys())

        added = source_keys - target_keys
        removed = target_keys - source_keys
        common = source_keys & target_keys

        modified = []
        identical = []

        for key in common:
            source_val = source['flattened_config'][key]
            target_val = target['flattened_config'][key]

            if source_val != target_val:
                modified.append({
                    'key': key,
                    'source_value': source_val,
                    'target_value': target_val
                })
            else:
                identical.append(key)

        return {
            'source': source_env,
            'target': target_env,
            'source_repo': source['repository'],
            'target_repo': target['repository'],
            'added': list(added),
            'removed': list(removed),
            'modified': modified,
            'identical': identical,
            'summary': {
                'added_count': len(added),
                'removed_count': len(removed),
                'modified_count': len(modified),
                'identical_count': len(identical)
            }
        }

    def get_repository_summary(self) -> Dict[str, Any]:
        """Get summary of all repositories"""
        summary = {
            'total_repos': len(self.repositories),
            'enabled_repos': len([r for r in self.repositories if r.get('enabled', True)]),
            'repositories': []
        }

        for repo in self.repositories:
            if not repo.get('enabled', True):
                continue

            envs = self.get_environments_by_repo(repo['name'])

            repo_summary = {
                'name': repo['name'],
                'path': repo['path'],
                'structure': repo['structure'],
                'environment_count': len(envs),
                'environments': [e['name'] for e in envs]
            }

            summary['repositories'].append(repo_summary)

        return summary
