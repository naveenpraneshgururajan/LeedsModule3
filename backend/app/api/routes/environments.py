"""
Environments API Routes

Endpoints for managing and viewing environment configurations.
"""

from fastapi import APIRouter, Request
from typing import Dict, Any

router = APIRouter()


@router.get("")
async def get_all_environments(request: Request) -> Dict[str, Any]:
    """
    Get all environments with metadata and health status.

    Returns:
        List of all environments with coverage and anomaly info
    """
    try:
        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector

        # Get all environments
        environments = parser.get_all_environments()

        # Add ML insights for each environment
        if ml_detector.is_ready():
            for env in environments:
                anomalies = ml_detector.detect_anomalies(env)
                env['coverage'] = anomalies.get('coverage', 0)
                env['anomaly_score'] = anomalies.get('anomaly_score', 0)
                env['is_anomaly'] = anomalies.get('is_anomaly', False)
                env['missing_keys'] = anomalies.get('missing_keys', [])
                env['missing_count'] = anomalies.get('missing_count', 0)

                # Determine health status
                coverage = env['coverage']
                if coverage >= 0.9:
                    env['health'] = 'healthy'
                elif coverage >= 0.75:
                    env['health'] = 'warning'
                else:
                    env['health'] = 'critical'

        # Sort by type and name
        environments.sort(key=lambda x: (x['type'], x['name']))

        return {
            "success": True,
            "data": environments,
            "count": len(environments)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/{env_name}")
async def get_environment(env_name: str, request: Request) -> Dict[str, Any]:
    """
    Get detailed information about a specific environment.

    Args:
        env_name: Environment name (e.g., "dev01")

    Returns:
        Detailed environment data with ML insights
    """
    try:
        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector
        change_tracker = request.app.state.change_tracker

        # Get environment data
        env = parser.get_environment(env_name)

        if not env:
            return {
                "success": False,
                "error": f"Environment '{env_name}' not found"
            }

        # Add ML insights
        if ml_detector.is_ready():
            anomalies = ml_detector.detect_anomalies(env)
            env['ml_insights'] = anomalies

            # Get similar environments
            all_envs = parser.get_all_environments()
            similar = ml_detector.get_similar_environments(env, all_envs)
            env['similar_environments'] = similar

        # Add change history
        if change_tracker.is_available():
            last_modified = change_tracker.get_last_modified(env['filename'])
            env['last_modified'] = last_modified

            history = change_tracker.get_file_history(env['filename'], limit=5)
            env['recent_history'] = history

        return {
            "success": True,
            "data": env
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/{env_name}/keys")
async def get_environment_keys(env_name: str, request: Request) -> Dict[str, Any]:
    """
    Get all keys in an environment.

    Args:
        env_name: Environment name

    Returns:
        List of all configuration keys
    """
    try:
        parser = request.app.state.parser

        env = parser.get_environment(env_name)

        if not env:
            return {
                "success": False,
                "error": f"Environment '{env_name}' not found"
            }

        keys = list(env['flattened_config'].keys())

        return {
            "success": True,
            "data": {
                "environment": env_name,
                "keys": keys,
                "count": len(keys)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/{env_name}/compare/{target_env}")
async def compare_environments(env_name: str, target_env: str, request: Request) -> Dict[str, Any]:
    """
    Compare two environments side-by-side.

    Args:
        env_name: Source environment name
        target_env: Target environment name

    Returns:
        Comparison results with added, removed, modified keys
    """
    try:
        parser = request.app.state.parser

        comparison = parser.compare(env_name, target_env)

        if 'error' in comparison:
            return {
                "success": False,
                "error": comparison['error']
            }

        return {
            "success": True,
            "data": comparison
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/types/summary")
async def get_environment_types_summary(request: Request) -> Dict[str, Any]:
    """
    Get summary grouped by environment type.

    Returns:
        Summary statistics by environment type (dev, cit, sit, etc.)
    """
    try:
        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector

        environments = parser.get_all_environments()

        # Group by type
        by_type = {}

        for env in environments:
            env_type = env['type']

            if env_type not in by_type:
                by_type[env_type] = {
                    'type': env_type,
                    'environments': [],
                    'count': 0,
                    'avg_coverage': 0,
                    'total_keys': 0
                }

            by_type[env_type]['environments'].append(env['name'])
            by_type[env_type]['count'] += 1
            by_type[env_type]['total_keys'] += env['total_keys']

        # Calculate averages with ML insights
        if ml_detector.is_ready():
            for env_type, data in by_type.items():
                coverages = []

                for env_name in data['environments']:
                    env = parser.get_environment(env_name)
                    if env:
                        anomalies = ml_detector.detect_anomalies(env)
                        coverages.append(anomalies.get('coverage', 0))

                if coverages:
                    data['avg_coverage'] = sum(coverages) / len(coverages)

        return {
            "success": True,
            "data": list(by_type.values())
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
