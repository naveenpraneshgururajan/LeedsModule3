"""
Reports API Routes

Endpoints for generating reports and analytics.
"""

from fastapi import APIRouter, Request, Query
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pathlib import Path

router = APIRouter()


@router.get("/coverage")
async def get_coverage_report(request: Request) -> Dict[str, Any]:
    """
    Get coverage report for all environments.

    Returns:
        Coverage matrix and statistics
    """
    try:
        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector

        environments = parser.get_all_environments()

        if not ml_detector.is_ready():
            return {
                "success": False,
                "error": "ML models not loaded"
            }

        # Get all unique keys
        all_keys = parser.get_all_unique_keys()

        # Build coverage matrix
        coverage_matrix = []

        for env in environments:
            env_keys = set(env['flattened_config'].keys())

            row = {
                'environment': env['name'],
                'type': env['type'],
                'total_keys': len(env_keys),
                'coverage': {},
                'overall_coverage': 0
            }

            # Check each key
            present_count = 0
            for key in all_keys[:100]:  # Limit to first 100 keys for matrix
                row['coverage'][key] = key in env_keys
                if key in env_keys:
                    present_count += 1

            row['overall_coverage'] = len(env_keys) / len(all_keys) if all_keys else 0

            coverage_matrix.append(row)

        # Calculate statistics by type
        by_type = {}

        for env in coverage_matrix:
            env_type = env['type']

            if env_type not in by_type:
                by_type[env_type] = {
                    'type': env_type,
                    'count': 0,
                    'avg_coverage': 0,
                    'coverages': []
                }

            by_type[env_type]['count'] += 1
            by_type[env_type]['coverages'].append(env['overall_coverage'])

        # Calculate averages
        for env_type, data in by_type.items():
            if data['coverages']:
                data['avg_coverage'] = sum(data['coverages']) / len(data['coverages'])
            del data['coverages']  # Remove temporary list

        return {
            "success": True,
            "data": {
                "coverage_matrix": coverage_matrix,
                "statistics_by_type": list(by_type.values()),
                "total_environments": len(environments),
                "total_unique_keys": len(all_keys),
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/anomalies")
async def get_anomalies_report(request: Request) -> Dict[str, Any]:
    """
    Get anomalies report across all environments.

    Returns:
        List of detected anomalies with details
    """
    try:
        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector

        if not ml_detector.is_ready():
            return {
                "success": False,
                "error": "ML models not loaded"
            }

        environments = parser.get_all_environments()
        anomalies = ml_detector.detect_anomalies_batch(environments)

        # Filter only anomalous environments
        anomalous_envs = [a for a in anomalies if a.get('is_anomaly', False)]

        # Sort by anomaly score
        anomalous_envs.sort(key=lambda x: x.get('anomaly_score', 0))

        return {
            "success": True,
            "data": {
                "anomalies": anomalous_envs,
                "total_anomalies": len(anomalous_envs),
                "total_environments": len(environments),
                "anomaly_rate": len(anomalous_envs) / len(environments) if environments else 0,
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/ml-status")
async def get_ml_status(request: Request) -> Dict[str, Any]:
    """
    Get ML model status and information.

    Returns:
        ML model status, accuracy, and metadata
    """
    try:
        ml_detector = request.app.state.ml_detector

        status = ml_detector.get_status()

        return {
            "success": True,
            "data": status
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/generate")
async def generate_report(request: Request) -> Dict[str, Any]:
    """
    Generate and save a report.

    Request body:
        {
            "type": "coverage" | "anomalies" | "full",
            "format": "json" | "html",
            "environments": ["dev01", "cit01"] // optional
        }

    Returns:
        Report data and saved file path
    """
    try:
        body = await request.json()

        report_type = body.get("type", "coverage")
        format_type = body.get("format", "json")
        env_filter = body.get("environments")

        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector

        # Generate report based on type
        if report_type == "coverage":
            # Get coverage data
            response = await get_coverage_report(request)
            report_data = response.get("data", {})

        elif report_type == "anomalies":
            # Get anomalies data
            response = await get_anomalies_report(request)
            report_data = response.get("data", {})

        elif report_type == "full":
            # Get both coverage and anomalies
            coverage_response = await get_coverage_report(request)
            anomalies_response = await get_anomalies_report(request)

            report_data = {
                "coverage": coverage_response.get("data", {}),
                "anomalies": anomalies_response.get("data", {}),
                "type": "full_report"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown report type: {report_type}"
            }

        # Filter by environments if specified
        if env_filter and isinstance(env_filter, list):
            # Apply filtering logic here if needed
            pass

        # Save report
        reports_dir = Path("./reports")
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report_type}_{timestamp}.{format_type}"
        filepath = reports_dir / filename

        if format_type == "json":
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)

        elif format_type == "html":
            # Generate simple HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Configuration Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <h1>Configuration Report - {report_type.title()}</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <pre>{json.dumps(report_data, indent=2)}</pre>
            </body>
            </html>
            """

            with open(filepath, 'w') as f:
                f.write(html)

        return {
            "success": True,
            "data": {
                "report": report_data,
                "file": str(filepath),
                "filename": filename,
                "format": format_type,
                "type": report_type
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/summary")
async def get_summary(request: Request) -> Dict[str, Any]:
    """
    Get high-level summary statistics.

    Returns:
        Dashboard summary with key metrics
    """
    try:
        parser = request.app.state.parser
        ml_detector = request.app.state.ml_detector
        change_tracker = request.app.state.change_tracker

        environments = parser.get_all_environments()

        # Calculate statistics
        total_envs = len(environments)
        all_keys = parser.get_all_unique_keys()
        total_keys = len(all_keys)

        # Group by type
        by_type = {}
        for env in environments:
            env_type = env['type']
            by_type[env_type] = by_type.get(env_type, 0) + 1

        # ML insights
        ml_status = ml_detector.get_status() if ml_detector else {}

        # Recent changes
        recent_changes_count = 0
        if change_tracker and change_tracker.is_available():
            recent_changes = change_tracker.get_recent_activity(days=7)
            recent_changes_count = len(recent_changes)

        # Coverage statistics
        coverages = []
        if ml_detector and ml_detector.is_ready():
            for env in environments:
                anomalies = ml_detector.detect_anomalies(env)
                coverages.append(anomalies.get('coverage', 0))

        avg_coverage = sum(coverages) / len(coverages) if coverages else 0

        return {
            "success": True,
            "data": {
                "total_environments": total_envs,
                "total_unique_keys": total_keys,
                "environments_by_type": by_type,
                "average_coverage": avg_coverage,
                "ml_loaded": ml_status.get('loaded', False),
                "recent_changes_count": recent_changes_count,
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
