"""
Uplift API Routes

Endpoints for uplift analysis and checklist generation.
"""

from fastapi import APIRouter, Request
from typing import Dict, Any

router = APIRouter()


@router.post("/analyze")
async def analyze_uplift(request: Request) -> Dict[str, Any]:
    """
    Analyze uplift requirements from source to target environment.

    Request body:
        {
            "source": "dev01",
            "target": "cit01",
            "since_date": "2024-01-15"  // optional
        }

    Returns:
        Uplift analysis with categorized recommendations
    """
    try:
        body = await request.json()

        source = body.get("source")
        target = body.get("target")
        since_date = body.get("since_date")

        if not source or not target:
            return {
                "success": False,
                "error": "Both 'source' and 'target' are required"
            }

        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector
        change_tracker = request.app.state.change_tracker
        uplift_assistant = request.app.state.uplift_assistant

        # Perform uplift analysis
        analysis = uplift_assistant.analyze(
            source_env=source,
            target_env=target,
            since_date=since_date,
            parser=parser,
            change_tracker=change_tracker,
            ml_detector=ml_detector
        )

        if 'error' in analysis:
            return {
                "success": False,
                "error": analysis['error']
            }

        return {
            "success": True,
            "data": analysis
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/checklist")
async def generate_checklist(request: Request) -> Dict[str, Any]:
    """
    Generate uplift checklist from analysis.

    Request body:
        {
            "source": "dev01",
            "target": "cit01",
            "since_date": "2024-01-15",  // optional
            "format": "markdown"  // markdown, text, or html
        }

    Returns:
        Generated checklist in specified format
    """
    try:
        body = await request.json()

        source = body.get("source")
        target = body.get("target")
        since_date = body.get("since_date")
        format_type = body.get("format", "markdown")

        if not source or not target:
            return {
                "success": False,
                "error": "Both 'source' and 'target' are required"
            }

        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector
        change_tracker = request.app.state.change_tracker
        uplift_assistant = request.app.state.uplift_assistant

        # Perform analysis
        analysis = uplift_assistant.analyze(
            source_env=source,
            target_env=target,
            since_date=since_date,
            parser=parser,
            change_tracker=change_tracker,
            ml_detector=ml_detector
        )

        if 'error' in analysis:
            return {
                "success": False,
                "error": analysis['error']
            }

        # Generate checklist
        checklist = uplift_assistant.generate_checklist(analysis, format=format_type)

        return {
            "success": True,
            "data": {
                "checklist": checklist,
                "format": format_type,
                "analysis": analysis
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/suggestions/{env_name}")
async def get_uplift_suggestions(env_name: str, request: Request) -> Dict[str, Any]:
    """
    Get suggested uplifts for an environment.

    Args:
        env_name: Environment name

    Returns:
        Suggested target environments for uplift
    """
    try:
        parser = request.app.state.parser
        uplift_assistant = request.app.state.uplift_assistant

        env = parser.get_environment(env_name)

        if not env:
            return {
                "success": False,
                "error": f"Environment '{env_name}' not found"
            }

        # Get environment type and suggest next level
        env_type = env['type']
        current_level = uplift_assistant.get_env_level(env_name)

        # Get all environments
        all_envs = parser.get_all_environments()

        # Find environments at the next level
        suggestions = []

        for target_env in all_envs:
            target_level = uplift_assistant.get_env_level(target_env['name'])

            # Suggest environments at the next level
            if target_level == current_level + 1:
                suggestions.append({
                    'environment': target_env['name'],
                    'type': target_env['type'],
                    'reason': f'Next level in hierarchy'
                })

        return {
            "success": True,
            "data": {
                "source": env_name,
                "source_type": env_type,
                "suggestions": suggestions
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/validate")
async def validate_uplift(request: Request) -> Dict[str, Any]:
    """
    Validate if an uplift is safe to proceed.

    Request body:
        {
            "source": "dev01",
            "target": "cit01"
        }

    Returns:
        Validation results with warnings and recommendations
    """
    try:
        body = await request.json()

        source = body.get("source")
        target = body.get("target")

        if not source or not target:
            return {
                "success": False,
                "error": "Both 'source' and 'target' are required"
            }

        parser = request.app.state.parser
        uplift_assistant = request.app.state.uplift_assistant

        # Check if environments exist
        source_env = parser.get_environment(source)
        target_env = parser.get_environment(target)

        if not source_env or not target_env:
            return {
                "success": False,
                "error": "One or both environments not found"
            }

        # Validate uplift direction
        valid_direction = uplift_assistant.is_valid_uplift_direction(source, target)

        warnings = []
        recommendations = []

        if not valid_direction:
            warnings.append({
                "type": "unusual_direction",
                "message": f"Uplifting from {source} to {target} is unusual",
                "severity": "medium"
            })
            recommendations.append("Verify this is the intended direction")

        # Check coverage
        source_keys = len(source_env['flattened_config'])
        target_keys = len(target_env['flattened_config'])

        if source_keys > target_keys * 1.5:
            warnings.append({
                "type": "large_difference",
                "message": f"Source has significantly more keys ({source_keys}) than target ({target_keys})",
                "severity": "medium"
            })
            recommendations.append("Review if all keys should be uplifted")

        # Overall validation
        is_safe = len([w for w in warnings if w['severity'] == 'high']) == 0

        return {
            "success": True,
            "data": {
                "is_safe": is_safe,
                "valid_direction": valid_direction,
                "warnings": warnings,
                "recommendations": recommendations,
                "source_keys": source_keys,
                "target_keys": target_keys
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
