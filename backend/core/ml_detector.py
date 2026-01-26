"""
ML Detector - Loads and uses pre-trained ML models

This module ONLY loads pre-trained models from disk.
NO training happens here - all training is done in ml-training/ module.
"""

import os
import json
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional


class MLDetector:
    def __init__(self, models_path: str = None):
        """
        Initialize ML detector by loading pre-trained models.

        Args:
            models_path: Path to models directory (default: ./models/)
        """
        self.models_path = Path(models_path or os.getenv('MODELS_PATH', './models'))

        # Model objects
        self.isolation_forest = None
        self.kmeans = None
        self.feature_names = []
        self.model_info = {}

        # Load models on initialization
        self.load_models()

    def load_models(self):
        """Load pre-trained models from disk"""
        try:
            # Load Isolation Forest
            if_path = self.models_path / "isolation_forest.pkl"
            if if_path.exists():
                self.isolation_forest = joblib.load(if_path)
                print(f"✅ Loaded Isolation Forest model from {if_path}")
            else:
                print(f"⚠️  Isolation Forest model not found at {if_path}")
                print("   Run: cd ml-training && python train_models.py")

            # Load KMeans
            kmeans_path = self.models_path / "kmeans_clusters.pkl"
            if kmeans_path.exists():
                self.kmeans = joblib.load(kmeans_path)
                print(f"✅ Loaded KMeans model from {kmeans_path}")
            else:
                print(f"⚠️  KMeans model not found at {kmeans_path}")

            # Load feature names
            features_path = self.models_path / "feature_names.json"
            if features_path.exists():
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
                print(f"✅ Loaded {len(self.feature_names)} feature names")
            else:
                print(f"⚠️  Feature names not found at {features_path}")

            # Load model info
            info_path = self.models_path / "model_info.json"
            if info_path.exists():
                with open(info_path, 'r') as f:
                    self.model_info = json.load(f)
                print(f"✅ Loaded model info (trained: {self.model_info.get('trained_date', 'unknown')})")
            else:
                print(f"⚠️  Model info not found at {info_path}")

        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.isolation_forest = None
            self.kmeans = None

    def is_ready(self) -> bool:
        """Check if models are loaded and ready"""
        return (self.isolation_forest is not None and
                self.kmeans is not None and
                len(self.feature_names) > 0)

    def get_status(self) -> Dict[str, Any]:
        """Get model status information"""
        return {
            'loaded': self.is_ready(),
            'isolation_forest_loaded': self.isolation_forest is not None,
            'kmeans_loaded': self.kmeans is not None,
            'num_features': len(self.feature_names),
            'model_info': self.model_info
        }

    def prepare_feature_vector(self, flattened_config: Dict[str, Any]) -> np.ndarray:
        """
        Prepare feature vector from flattened configuration.

        Args:
            flattened_config: Flattened configuration dictionary

        Returns:
            Feature vector as numpy array
        """
        if not self.feature_names:
            return np.array([])

        # Create binary feature vector: 1 if key exists, 0 if missing
        features = [1 if key in flattened_config else 0 for key in self.feature_names]
        return np.array(features).reshape(1, -1)

    def detect_anomalies(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomalies in environment configuration using ML.

        Args:
            env_data: Environment data from parser

        Returns:
            Anomaly detection results
        """
        if not self.is_ready():
            return {
                'error': 'Models not loaded',
                'loaded': False
            }

        try:
            flattened = env_data.get('flattened_config', {})

            # Prepare feature vector
            X = self.prepare_feature_vector(flattened)

            if X.size == 0:
                return {'error': 'Could not prepare features'}

            # Get anomaly score
            anomaly_score = self.isolation_forest.decision_function(X)[0]
            is_anomaly = self.isolation_forest.predict(X)[0] == -1

            # Get cluster assignment
            cluster = int(self.kmeans.predict(X)[0])

            # Find missing keys (keys in training data but not in this config)
            env_keys = set(flattened.keys())
            training_keys = set(self.feature_names)
            missing_keys = list(training_keys - env_keys)

            # Calculate confidence (inverse of anomaly score, normalized)
            confidence = float(1 / (1 + abs(anomaly_score)))

            return {
                'environment': env_data.get('name', 'unknown'),
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(anomaly_score),
                'confidence': confidence,
                'cluster': cluster,
                'missing_keys': missing_keys,
                'missing_count': len(missing_keys),
                'present_keys_count': len(env_keys),
                'expected_keys_count': len(training_keys),
                'coverage': len(env_keys) / len(training_keys) if training_keys else 0
            }

        except Exception as e:
            return {
                'error': f'Error detecting anomalies: {str(e)}',
                'environment': env_data.get('name', 'unknown')
            }

    def detect_anomalies_batch(self, environments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies for multiple environments.

        Args:
            environments: List of environment data dictionaries

        Returns:
            List of anomaly detection results
        """
        results = []
        for env in environments:
            result = self.detect_anomalies(env)
            results.append(result)

        return results

    def get_similar_environments(self, env_data: Dict[str, Any], all_environments: List[Dict[str, Any]]) -> List[str]:
        """
        Find environments in the same cluster (similar configurations).

        Args:
            env_data: Target environment data
            all_environments: List of all environment data

        Returns:
            List of similar environment names
        """
        if not self.is_ready():
            return []

        try:
            # Get cluster for target environment
            X_target = self.prepare_feature_vector(env_data.get('flattened_config', {}))
            target_cluster = int(self.kmeans.predict(X_target)[0])

            # Find all environments in the same cluster
            similar = []
            for env in all_environments:
                if env['name'] == env_data['name']:
                    continue

                X_env = self.prepare_feature_vector(env.get('flattened_config', {}))
                env_cluster = int(self.kmeans.predict(X_env)[0])

                if env_cluster == target_cluster:
                    similar.append(env['name'])

            return similar

        except Exception as e:
            print(f"Error finding similar environments: {e}")
            return []

    def should_have_key(self, env_type: str, key: str) -> Dict[str, Any]:
        """
        Predict if an environment type should have a specific key.

        Args:
            env_type: Environment type (dev, cit, sit, luat, prod)
            key: Configuration key

        Returns:
            Prediction with confidence
        """
        if key not in self.feature_names:
            return {
                'should_have': True,  # New keys should be uplifted
                'confidence': 0.5,
                'reason': 'New key not in training data'
            }

        # Simple heuristic based on environment type
        # In production, this could be more sophisticated
        env_hierarchy = ['dev', 'cit', 'sit', 'luat', 'prod']

        if env_type in ['prod', 'luat']:
            # Production and LUAT should have most keys
            return {
                'should_have': True,
                'confidence': 0.9,
                'reason': f'{env_type.upper()} environment should have all keys'
            }
        elif env_type == 'sit':
            return {
                'should_have': True,
                'confidence': 0.85,
                'reason': 'SIT environment should have most keys'
            }
        elif env_type == 'cit':
            return {
                'should_have': True,
                'confidence': 0.8,
                'reason': 'CIT environment should have most keys'
            }
        else:  # dev
            return {
                'should_have': True,
                'confidence': 0.6,
                'reason': 'DEV environment can have experimental keys'
            }
