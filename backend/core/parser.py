"""
YAML Configuration Parser

Reads and parses YAML configuration files from local filesystem.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class YAMLParser:
    def __init__(self, yaml_path: Optional[str] = None):
        """
        Initialize parser with path to YAML files.

        Args:
            yaml_path: Path to directory containing YAML files.
                      If None, reads from environment variable.
        """
        self.yaml_path = yaml_path or os.getenv('YAML_FILES_PATH', '/path/to/configs')
        self.yaml_dir = Path(self.yaml_path)

        if not self.yaml_dir.exists():
            print(f"Warning: YAML directory not found: {self.yaml_path}")

    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        Flatten nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key for recursion
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def load_yaml_file(self, filename: str) -> Optional[Dict]:
        """
        Load a single YAML file.

        Args:
            filename: Name of the YAML file

        Returns:
            Parsed YAML content or None if error
        """
        file_path = self.yaml_dir / filename

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
                return content if content else {}
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None

    def get_all_yaml_files(self) -> List[str]:
        """
        Get list of all YAML files in directory.

        Returns:
            List of YAML filenames
        """
        if not self.yaml_dir.exists():
            return []

        yaml_files = []
        for file_path in self.yaml_dir.glob("env-*.yaml"):
            yaml_files.append(file_path.name)

        # Also check for .yml extension
        for file_path in self.yaml_dir.glob("env-*.yml"):
            yaml_files.append(file_path.name)

        return sorted(yaml_files)

    def get_environment_name(self, filename: str) -> str:
        """
        Extract environment name from filename.

        Args:
            filename: e.g., "env-dev01.yaml"

        Returns:
            Environment name, e.g., "dev01"
        """
        # Remove env- prefix and .yaml/.yml suffix
        name = filename.replace('env-', '').replace('.yaml', '').replace('.yml', '')
        return name

    def get_environment_type(self, env_name: str) -> str:
        """
        Determine environment type from name.

        Args:
            env_name: e.g., "dev01", "cit02"

        Returns:
            Environment type: "dev", "cit", "sit", "luat", "prod"
        """
        name_lower = env_name.lower()

        if name_lower.startswith('dev'):
            return 'dev'
        elif name_lower.startswith('cit'):
            return 'cit'
        elif name_lower.startswith('sit'):
            return 'sit'
        elif name_lower.startswith('luat'):
            return 'luat'
        elif name_lower.startswith('desktop'):
            return 'prod'
        else:
            return 'unknown'

    def get_all_environments(self) -> List[Dict[str, Any]]:
        """
        Get all environments with metadata.

        Returns:
            List of environment dictionaries
        """
        environments = []
        yaml_files = self.get_all_yaml_files()

        for filename in yaml_files:
            env_name = self.get_environment_name(filename)
            env_type = self.get_environment_type(env_name)
            content = self.load_yaml_file(filename)

            if content is not None:
                flattened = self.flatten_dict(content)

                env_data = {
                    'name': env_name,
                    'filename': filename,
                    'type': env_type,
                    'total_keys': len(flattened),
                    'config': content,
                    'flattened_config': flattened
                }
                environments.append(env_data)

        return environments

    def get_environment(self, env_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific environment data.

        Args:
            env_name: Environment name (e.g., "dev01")

        Returns:
            Environment data dictionary or None
        """
        # Try with different filename patterns
        possible_filenames = [
            f"env-{env_name}.yaml",
            f"env-{env_name}.yml",
            f"{env_name}.yaml",
            f"{env_name}.yml"
        ]

        for filename in possible_filenames:
            content = self.load_yaml_file(filename)
            if content is not None:
                flattened = self.flatten_dict(content)
                env_type = self.get_environment_type(env_name)

                return {
                    'name': env_name,
                    'filename': filename,
                    'type': env_type,
                    'total_keys': len(flattened),
                    'config': content,
                    'flattened_config': flattened
                }

        return None

    def get_all_unique_keys(self) -> List[str]:
        """
        Get all unique keys across all environments.

        Returns:
            Sorted list of unique keys
        """
        all_keys = set()
        environments = self.get_all_environments()

        for env in environments:
            all_keys.update(env['flattened_config'].keys())

        return sorted(list(all_keys))

    def compare(self, source_env: str, target_env: str) -> Dict[str, Any]:
        """
        Compare two environments.

        Args:
            source_env: Source environment name
            target_env: Target environment name

        Returns:
            Comparison result with added, removed, modified, identical keys
        """
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

        added = source_keys - target_keys  # In source but not in target
        removed = target_keys - source_keys  # In target but not in source
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

    def get_missing_keys(self, env_name: str, reference_keys: List[str]) -> List[str]:
        """
        Get keys missing in an environment compared to reference.

        Args:
            env_name: Environment to check
            reference_keys: List of keys that should exist

        Returns:
            List of missing keys
        """
        env = self.get_environment(env_name)
        if not env:
            return []

        env_keys = set(env['flattened_config'].keys())
        missing = [key for key in reference_keys if key not in env_keys]

        return missing
