"""
Backend Configuration

Loads configuration from environment variables.
"""

import os
from pathlib import Path


class Settings:
    """Application settings"""

    # Paths
    YAML_FILES_PATH: str = os.getenv("YAML_FILES_PATH", "/path/to/your/configs")
    GIT_REPO_PATH: str = os.getenv("GIT_REPO_PATH", "/path/to/your/configs")
    MODELS_PATH: str = os.getenv("MODELS_PATH", "./models")

    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # ML Settings
    ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.7"))
    DEV_LENIENCY: float = float(os.getenv("DEV_LENIENCY", "0.5"))

    # Storage
    STORAGE_PATH: str = "./storage"
    REPORTS_PATH: str = "./reports"

    def __init__(self):
        """Initialize settings and create directories"""
        # Ensure directories exist
        Path(self.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.REPORTS_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.MODELS_PATH).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
