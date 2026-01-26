"""
Changes API Routes

Endpoints for tracking configuration changes via git history.
"""

from fastapi import APIRouter, Request, Query
from typing import Dict, Any, Optional

router = APIRouter()


@router.get("")
async def get_changes(
    request: Request,
    env: Optional[str] = Query(None, description="Filter by environment name"),
    since: Optional[str] = Query(None, description="Date to start from (YYYY-MM-DD)"),
    limit: Optional[int] = Query(50, description="Maximum number of changes")
) -> Dict[str, Any]:
    """
    Get change history for configurations.

    Query params:
        env: Filter by environment name (e.g., "dev01")
        since: ISO date string (e.g., "2024-01-15")
        limit: Maximum number of changes to return

    Returns:
        List of changes with metadata
    """
    try:
        change_tracker = request.app.state.change_tracker

        if not change_tracker.is_available():
            return {
                "success": False,
                "error": "Change tracking not available (git not configured)"
            }

        # Get changes
        if since:
            changes = change_tracker.get_changes_since(since)
        else:
            # Default to last 30 days
            changes = change_tracker.get_recent_activity(days=30)

        # Filter by environment if specified
        if env and changes:
            changes = [c for c in changes if c.get('environment') == env]

        # Limit results
        if limit and len(changes) > limit:
            changes = changes[:limit]

        return {
            "success": True,
            "data": changes,
            "count": len(changes),
            "filtered_by": {
                "environment": env,
                "since": since
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/recent")
async def get_recent_changes(
    request: Request,
    days: int = Query(7, description="Number of days to look back")
) -> Dict[str, Any]:
    """
    Get recent changes across all environments.

    Query params:
        days: Number of days to look back (default: 7)

    Returns:
        Recent changes
    """
    try:
        change_tracker = request.app.state.change_tracker

        if not change_tracker.is_available():
            return {
                "success": False,
                "error": "Change tracking not available"
            }

        changes = change_tracker.get_recent_activity(days=days)

        return {
            "success": True,
            "data": changes,
            "count": len(changes),
            "days": days
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/history/{env_name}")
async def get_environment_history(
    env_name: str,
    request: Request,
    limit: int = Query(10, description="Maximum number of commits")
) -> Dict[str, Any]:
    """
    Get commit history for a specific environment.

    Args:
        env_name: Environment name

    Query params:
        limit: Maximum number of commits to return

    Returns:
        Commit history for the environment
    """
    try:
        change_tracker = request.app.state.change_tracker

        if not change_tracker.is_available():
            return {
                "success": False,
                "error": "Change tracking not available"
            }

        # Try different filename patterns
        filenames = [
            f"env-{env_name}.yaml",
            f"env-{env_name}.yml"
        ]

        history = []
        for filename in filenames:
            history = change_tracker.get_file_history(filename, limit=limit)
            if history:
                break

        return {
            "success": True,
            "data": {
                "environment": env_name,
                "history": history,
                "count": len(history)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/diff/{env_name}")
async def get_environment_diff(
    env_name: str,
    request: Request,
    commit: str = Query("HEAD", description="Commit hash")
) -> Dict[str, Any]:
    """
    Get diff for an environment at a specific commit.

    Args:
        env_name: Environment name

    Query params:
        commit: Commit hash (default: HEAD)

    Returns:
        Diff output
    """
    try:
        change_tracker = request.app.state.change_tracker

        if not change_tracker.is_available():
            return {
                "success": False,
                "error": "Change tracking not available"
            }

        filename = f"env-{env_name}.yaml"
        diff = change_tracker.get_file_diff(filename, commit_hash=commit)

        if diff is None:
            return {
                "success": False,
                "error": f"Could not get diff for {env_name}"
            }

        return {
            "success": True,
            "data": {
                "environment": env_name,
                "commit": commit,
                "diff": diff
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/compare-history")
async def compare_history(
    request: Request,
    env1: str = Query(..., description="First environment"),
    env2: str = Query(..., description="Second environment")
) -> Dict[str, Any]:
    """
    Compare change history between two environments.

    Query params:
        env1: First environment name
        env2: Second environment name

    Returns:
        Comparison of change history
    """
    try:
        change_tracker = request.app.state.change_tracker

        if not change_tracker.is_available():
            return {
                "success": False,
                "error": "Change tracking not available"
            }

        comparison = change_tracker.get_changes_between(env1, env2)

        return {
            "success": True,
            "data": comparison
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/status")
async def get_git_status(request: Request) -> Dict[str, Any]:
    """
    Get git repository status.

    Returns:
        Git repository status and statistics
    """
    try:
        change_tracker = request.app.state.change_tracker

        status = change_tracker.get_status()

        return {
            "success": True,
            "data": status
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
