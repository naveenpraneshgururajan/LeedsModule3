"""
Repositories API Routes

Endpoints for managing multiple repositories.
"""

from fastapi import APIRouter, Request
from typing import Dict, Any

router = APIRouter()


@router.get("/summary")
async def get_repositories_summary(request: Request) -> Dict[str, Any]:
    """
    Get summary of all configured repositories.

    Returns:
        Summary with repository count and details
    """
    try:
        # Check if multi-repo parser is available
        parser = request.app.state.parser

        if hasattr(parser, 'get_repository_summary'):
            # Multi-repo mode
            summary = parser.get_repository_summary()
            return {
                "success": True,
                "mode": "multi-repo",
                "data": summary
            }
        else:
            # Single-repo mode (backward compatibility)
            envs = parser.get_all_environments()
            return {
                "success": True,
                "mode": "single-repo",
                "data": {
                    "total_repos": 1,
                    "enabled_repos": 1,
                    "repositories": [
                        {
                            "name": "default",
                            "path": parser.yaml_path,
                            "structure": "simple",
                            "environment_count": len(envs),
                            "environments": [e['name'] for e in envs]
                        }
                    ]
                }
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/list")
async def list_repositories(request: Request) -> Dict[str, Any]:
    """
    List all configured repositories.

    Returns:
        List of repositories with their configurations
    """
    try:
        parser = request.app.state.parser

        if hasattr(parser, 'repositories'):
            # Multi-repo mode
            repos = []
            for repo in parser.repositories:
                repos.append({
                    "name": repo['name'],
                    "path": repo['path'],
                    "enabled": repo.get('enabled', True),
                    "structure": repo.get('structure', 'simple')
                })

            return {
                "success": True,
                "data": repos,
                "count": len(repos)
            }
        else:
            # Single-repo mode
            return {
                "success": True,
                "data": [
                    {
                        "name": "default",
                        "path": parser.yaml_path,
                        "enabled": True,
                        "structure": "simple"
                    }
                ],
                "count": 1
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/{repo_name}/environments")
async def get_repository_environments(repo_name: str, request: Request) -> Dict[str, Any]:
    """
    Get all environments from a specific repository.

    Args:
        repo_name: Repository name

    Returns:
        List of environments from the specified repository
    """
    try:
        parser = request.app.state.parser

        if hasattr(parser, 'get_environments_by_repo'):
            # Multi-repo mode
            envs = parser.get_environments_by_repo(repo_name)

            return {
                "success": True,
                "data": envs,
                "count": len(envs),
                "repository": repo_name
            }
        else:
            # Single-repo mode - return all if repo_name matches "default"
            if repo_name == "default":
                envs = parser.get_all_environments()
                return {
                    "success": True,
                    "data": envs,
                    "count": len(envs),
                    "repository": "default"
                }
            else:
                return {
                    "success": False,
                    "error": f"Repository '{repo_name}' not found (single-repo mode)"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
