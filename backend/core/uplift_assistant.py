"""
Uplift Assistant - Intelligent uplift recommendations

Analyzes configurations and provides recommendations for uplifting changes
from lower environments to higher environments.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class UpliftAssistant:
    def __init__(self):
        """Initialize uplift assistant"""
        # Environment hierarchy (order matters)
        self.env_hierarchy = {
            'dev': 1,
            'cit': 2,
            'sit': 3,
            'luat': 4,
            'prod': 5
        }

        # Critical keys that should always be uplifted
        self.critical_patterns = [
            'auth',
            'security',
            'api_key',
            'endpoint',
            'url',
            'service'
        ]

    def get_env_level(self, env_name: str) -> int:
        """Get hierarchical level of environment"""
        env_lower = env_name.lower()

        for env_type, level in self.env_hierarchy.items():
            if env_lower.startswith(env_type):
                return level

        return 0  # Unknown

    def is_valid_uplift_direction(self, source: str, target: str) -> bool:
        """
        Check if uplift direction is valid (lower to higher environment).

        Args:
            source: Source environment name
            target: Target environment name

        Returns:
            True if valid uplift direction
        """
        source_level = self.get_env_level(source)
        target_level = self.get_env_level(target)

        return source_level < target_level

    def is_critical_key(self, key: str) -> bool:
        """
        Determine if a key is critical and should always be uplifted.

        Args:
            key: Configuration key

        Returns:
            True if critical
        """
        key_lower = key.lower()

        for pattern in self.critical_patterns:
            if pattern in key_lower:
                return True

        return False

    def categorize_change(self, key: str, source_val: Any, target_val: Any,
                         in_source: bool, in_target: bool) -> str:
        """
        Categorize a configuration change.

        Args:
            key: Configuration key
            source_val: Value in source
            target_val: Value in target
            in_source: Key exists in source
            in_target: Key exists in target

        Returns:
            Category: "critical", "recommended", "optional"
        """
        # Missing in target but present in source
        if in_source and not in_target:
            if self.is_critical_key(key):
                return "critical"
            else:
                return "recommended"

        # Different values
        if in_source and in_target and source_val != target_val:
            if self.is_critical_key(key):
                return "critical"
            else:
                return "recommended"

        # Dev-specific keys (may not need uplift)
        if key.lower().startswith('debug') or 'test' in key.lower():
            return "optional"

        return "optional"

    def analyze(self, source_env: str, target_env: str,
                since_date: Optional[str] = None,
                parser=None, change_tracker=None, ml_detector=None) -> Dict[str, Any]:
        """
        Analyze uplift requirements from source to target environment.

        Args:
            source_env: Source environment name
            target_env: Target environment name
            since_date: Optional date to filter changes
            parser: YAMLParser instance
            change_tracker: ChangeTracker instance
            ml_detector: MLDetector instance

        Returns:
            Uplift analysis with categorized recommendations
        """
        result = {
            'source': source_env,
            'target': target_env,
            'valid_direction': self.is_valid_uplift_direction(source_env, target_env),
            'analyzed_at': datetime.now().isoformat(),
            'critical': [],
            'recommended': [],
            'optional': [],
            'summary': {}
        }

        # Check if uplift direction is valid
        if not result['valid_direction']:
            result['warning'] = f"Unusual uplift direction: {source_env} → {target_env}"

        # If parser not provided, return basic result
        if not parser:
            result['error'] = 'Parser not provided'
            return result

        # Get environment data
        source_data = parser.get_environment(source_env)
        target_data = parser.get_environment(target_env)

        if not source_data or not target_data:
            result['error'] = 'One or both environments not found'
            result['source_found'] = source_data is not None
            result['target_found'] = target_data is not None
            return result

        # Compare configurations
        comparison = parser.compare(source_env, target_env)

        # Get changes since date if provided
        recent_changes = []
        if change_tracker and change_tracker.is_available() and since_date:
            all_changes = change_tracker.get_changes_since(since_date)
            # Filter for source environment
            recent_changes = [
                c for c in all_changes
                if c.get('environment') == source_env
            ]

        # Get ML insights if available
        ml_insights = {}
        if ml_detector and ml_detector.is_ready():
            source_anomalies = ml_detector.detect_anomalies(source_data)
            target_anomalies = ml_detector.detect_anomalies(target_data)
            ml_insights = {
                'source_coverage': source_anomalies.get('coverage', 0),
                'target_coverage': target_anomalies.get('coverage', 0),
                'target_missing_count': target_anomalies.get('missing_count', 0)
            }

        # Analyze keys added in source (missing in target)
        for key in comparison['added']:
            source_val = source_data['flattened_config'][key]
            category = self.categorize_change(key, source_val, None, True, False)

            # Check if recently changed
            recently_changed = False
            change_date = None
            for change in recent_changes:
                if key in str(change):
                    recently_changed = True
                    change_date = change.get('date')
                    break

            # ML confidence
            ml_confidence = 0.8  # Default
            if ml_detector and ml_detector.is_ready():
                prediction = ml_detector.should_have_key(
                    target_data['type'], key
                )
                ml_confidence = prediction.get('confidence', 0.8)

            item = {
                'key': key,
                'status': 'missing_in_target',
                'source_value': source_val,
                'target_value': None,
                'recently_changed': recently_changed,
                'change_date': change_date,
                'ml_confidence': ml_confidence,
                'is_critical': self.is_critical_key(key)
            }

            if category == 'critical':
                result['critical'].append(item)
            elif category == 'recommended':
                result['recommended'].append(item)
            else:
                result['optional'].append(item)

        # Analyze modified keys
        for mod in comparison['modified']:
            key = mod['key']
            category = self.categorize_change(
                key, mod['source_value'], mod['target_value'], True, True
            )

            # Check if recently changed
            recently_changed = False
            change_date = None
            for change in recent_changes:
                if key in str(change):
                    recently_changed = True
                    change_date = change.get('date')
                    break

            item = {
                'key': key,
                'status': 'different_values',
                'source_value': mod['source_value'],
                'target_value': mod['target_value'],
                'recently_changed': recently_changed,
                'change_date': change_date,
                'ml_confidence': 0.75,
                'is_critical': self.is_critical_key(key)
            }

            if category == 'critical':
                result['critical'].append(item)
            elif category == 'recommended':
                result['recommended'].append(item)
            else:
                result['optional'].append(item)

        # Add summary
        result['summary'] = {
            'critical_count': len(result['critical']),
            'recommended_count': len(result['recommended']),
            'optional_count': len(result['optional']),
            'total_items': len(result['critical']) + len(result['recommended']) + len(result['optional']),
            'recent_changes_count': len(recent_changes),
            'ml_insights': ml_insights
        }

        return result

    def generate_checklist(self, analysis: Dict[str, Any], format: str = 'markdown') -> str:
        """
        Generate uplift checklist from analysis.

        Args:
            analysis: Analysis result from analyze()
            format: Output format ('markdown', 'text', 'html')

        Returns:
            Formatted checklist string
        """
        if format == 'markdown':
            return self._generate_markdown_checklist(analysis)
        elif format == 'html':
            return self._generate_html_checklist(analysis)
        else:
            return self._generate_text_checklist(analysis)

    def _generate_markdown_checklist(self, analysis: Dict[str, Any]) -> str:
        """Generate markdown formatted checklist"""
        lines = []
        lines.append(f"# Uplift Checklist: {analysis['source']} → {analysis['target']}")
        lines.append(f"\nGenerated: {analysis['analyzed_at']}")
        lines.append(f"\n## Summary")
        lines.append(f"- Critical items: {analysis['summary']['critical_count']}")
        lines.append(f"- Recommended items: {analysis['summary']['recommended_count']}")
        lines.append(f"- Optional items: {analysis['summary']['optional_count']}")
        lines.append(f"- Total: {analysis['summary']['total_items']}")

        if analysis['critical']:
            lines.append(f"\n## 🔴 Critical Items ({len(analysis['critical'])})")
            for item in analysis['critical']:
                lines.append(f"\n### [ ] {item['key']}")
                lines.append(f"- Status: {item['status']}")
                lines.append(f"- Source value: `{item['source_value']}`")
                if item['target_value'] is not None:
                    lines.append(f"- Target value: `{item['target_value']}`")
                if item['recently_changed']:
                    lines.append(f"- Recently changed: {item['change_date']}")

        if analysis['recommended']:
            lines.append(f"\n## 🟡 Recommended Items ({len(analysis['recommended'])})")
            for item in analysis['recommended']:
                lines.append(f"\n### [ ] {item['key']}")
                lines.append(f"- Status: {item['status']}")
                lines.append(f"- Source value: `{item['source_value']}`")
                if item['target_value'] is not None:
                    lines.append(f"- Target value: `{item['target_value']}`")

        if analysis['optional']:
            lines.append(f"\n## 🟢 Optional Items ({len(analysis['optional'])})")
            for item in analysis['optional']:
                lines.append(f"- [ ] {item['key']}")

        return '\n'.join(lines)

    def _generate_text_checklist(self, analysis: Dict[str, Any]) -> str:
        """Generate plain text checklist"""
        lines = []
        lines.append(f"Uplift Checklist: {analysis['source']} → {analysis['target']}")
        lines.append("=" * 60)
        lines.append(f"\nCritical items: {analysis['summary']['critical_count']}")
        lines.append(f"Recommended items: {analysis['summary']['recommended_count']}")
        lines.append(f"Optional items: {analysis['summary']['optional_count']}")

        if analysis['critical']:
            lines.append(f"\n\nCRITICAL ITEMS:")
            lines.append("-" * 60)
            for item in analysis['critical']:
                lines.append(f"\n[ ] {item['key']}")
                lines.append(f"    {item['status']}")
                lines.append(f"    Source: {item['source_value']}")

        if analysis['recommended']:
            lines.append(f"\n\nRECOMMENDED ITEMS:")
            lines.append("-" * 60)
            for item in analysis['recommended']:
                lines.append(f"[ ] {item['key']}")

        return '\n'.join(lines)

    def _generate_html_checklist(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML checklist"""
        # Simple HTML generation
        html = f"""
        <h1>Uplift Checklist: {analysis['source']} → {analysis['target']}</h1>
        <p>Generated: {analysis['analyzed_at']}</p>
        <h2>Summary</h2>
        <ul>
            <li>Critical: {analysis['summary']['critical_count']}</li>
            <li>Recommended: {analysis['summary']['recommended_count']}</li>
            <li>Optional: {analysis['summary']['optional_count']}</li>
        </ul>
        """

        if analysis['critical']:
            html += "<h2>🔴 Critical Items</h2><ul>"
            for item in analysis['critical']:
                html += f"<li><input type='checkbox'> {item['key']}"
                html += f"<br>Status: {item['status']}"
                html += f"<br>Source: <code>{item['source_value']}</code></li>"
            html += "</ul>"

        return html
