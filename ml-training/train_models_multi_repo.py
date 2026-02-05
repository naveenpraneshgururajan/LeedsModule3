#!/usr/bin/env python3
"""
ML Model Training Script - Multi-Repository Support

This script trains machine learning models for configuration anomaly detection
across multiple repositories with different structures.
"""

import os
import sys
import yaml
import json
import joblib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path to import multi_repo_parser
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

from backend.core.multi_repo_parser import MultiRepoParser


class MultiRepoConfigTrainer:
    def __init__(self, repos_config_path: str = "../repositories.yaml"):
        """Initialize trainer with repositories configuration"""
        self.repos_config_path = repos_config_path
        self.parser = MultiRepoParser(repos_config_path)
        self.output_path = Path("../backend/models")
        self.output_path.mkdir(parents=True, exist_ok=True)

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

    def extract_features(self, environments: List[Dict[str, Any]]) -> tuple:
        """Extract features from environments for ML training"""
        print("\n📊 Extracting features...")

        # Get all unique keys across all environments and repos
        all_keys = set()
        flattened_configs = {}

        for env in environments:
            env_id = f"{env['repository']}.{env['name']}"
            flattened = env['flattened_config']
            flattened_configs[env_id] = flattened
            all_keys.update(flattened.keys())

        all_keys = sorted(list(all_keys))
        print(f"  ✓ Found {len(all_keys)} unique keys across all repos")

        # Create feature matrix: rows = environments, columns = keys (binary)
        feature_matrix = []
        env_identifiers = []

        for env_id, flattened in flattened_configs.items():
            features = [1 if key in flattened else 0 for key in all_keys]
            feature_matrix.append(features)
            env_identifiers.append(env_id)

        df = pd.DataFrame(feature_matrix, columns=all_keys, index=env_identifiers)
        print(f"  ✓ Created feature matrix: {df.shape[0]} environments × {df.shape[1]} features")

        return df, all_keys

    def train_isolation_forest(self, X: np.ndarray) -> IsolationForest:
        """Train Isolation Forest for anomaly detection"""
        print("\n🌲 Training Isolation Forest...")

        model = IsolationForest(
            contamination=0.1,
            n_estimators=100,
            random_state=42
        )

        model.fit(X)

        # Get anomaly scores
        scores = model.decision_function(X)
        predictions = model.predict(X)

        n_anomalies = sum(predictions == -1)
        print(f"  ✓ Model trained successfully")
        print(f"  ✓ Detected {n_anomalies} potential anomalies")

        return model

    def train_kmeans(self, X: np.ndarray) -> KMeans:
        """Train KMeans for environment clustering"""
        print("\n🎯 Training KMeans Clustering...")

        # Determine optimal number of clusters (min of 5 or number of envs)
        n_clusters = min(5, X.shape[0])

        model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            max_iter=300
        )

        model.fit(X)

        print(f"  ✓ Model trained successfully")
        print(f"  ✓ Created {n_clusters} clusters")

        return model

    def save_models(self, isolation_forest, kmeans, feature_names: List[str],
                    env_identifiers: List[str], repo_summary: Dict):
        """Save trained models and metadata"""
        print("\n💾 Saving models...")

        # Save Isolation Forest
        if_path = self.output_path / "isolation_forest.pkl"
        joblib.dump(isolation_forest, if_path)
        print(f"  ✓ Saved: {if_path}")

        # Save KMeans
        kmeans_path = self.output_path / "kmeans_clusters.pkl"
        joblib.dump(kmeans, kmeans_path)
        print(f"  ✓ Saved: {kmeans_path}")

        # Save feature names
        features_path = self.output_path / "feature_names.json"
        with open(features_path, 'w') as f:
            json.dump(feature_names, f, indent=2)
        print(f"  ✓ Saved: {features_path}")

        # Save model info with repository details
        model_info = {
            "trained_date": datetime.now().isoformat(),
            "num_environments": len(env_identifiers),
            "num_features": len(feature_names),
            "version": "2.0.0-multi-repo",
            "trained_on_environments": env_identifiers,
            "repositories": repo_summary,
            "isolation_forest_params": {
                "contamination": 0.1,
                "n_estimators": 100,
                "random_state": 42
            },
            "kmeans_params": {
                "n_clusters": kmeans.n_clusters,
                "random_state": 42,
                "max_iter": 300
            }
        }

        info_path = self.output_path / "model_info.json"
        with open(info_path, 'w') as f:
            json.dump(model_info, f, indent=2)
        print(f"  ✓ Saved: {info_path}")

    def train(self):
        """Main training pipeline for multi-repository setup"""
        print("=" * 70)
        print("🤖 ML Model Training Pipeline - Multi-Repository Support")
        print("=" * 70)

        # Get repository summary
        print("\n📂 Repository Configuration:")
        repo_summary = self.parser.get_repository_summary()
        print(f"   Total repositories: {repo_summary['total_repos']}")
        print(f"   Enabled repositories: {repo_summary['enabled_repos']}")

        for repo in repo_summary['repositories']:
            print(f"\n   📁 {repo['name']}:")
            print(f"      Path: {repo['path']}")
            print(f"      Structure: {repo['structure']}")
            print(f"      Environments: {repo['environment_count']}")
            print(f"      Names: {', '.join(repo['environments'][:5])}" +
                  (f" (and {len(repo['environments']) - 5} more)" if len(repo['environments']) > 5 else ""))

        # Load all environments
        print("\n📂 Loading environments from all repositories...")
        environments = self.parser.get_all_environments()

        if len(environments) < 3:
            print("\n⚠️  Warning: Less than 3 environments found.")
            print("   Need at least 3 environments for accurate training.")
            print("\n💡 Check your repositories.yaml configuration:")
            print("   - Verify repository paths exist")
            print("   - Check that repositories are enabled")
            print("   - Ensure YAML files match the patterns")
            sys.exit(1)

        # Extract features
        df, feature_names = self.extract_features(environments)
        X = df.values

        # Train models
        isolation_forest = self.train_isolation_forest(X)
        kmeans = self.train_kmeans(X)

        # Save everything
        self.save_models(
            isolation_forest,
            kmeans,
            feature_names,
            df.index.tolist(),
            repo_summary
        )

        print("\n" + "=" * 70)
        print("✅ Training Complete!")
        print("=" * 70)
        print(f"\nModels saved to: {self.output_path.absolute()}")
        print(f"\nTraining Statistics:")
        print(f"  - Total environments: {len(environments)}")
        print(f"  - Total repositories: {repo_summary['enabled_repos']}")
        print(f"  - Total unique keys: {len(feature_names)}")
        print(f"  - Model version: 2.0.0-multi-repo")

        print("\n🎯 Next steps:")
        print("  1. Models are ready to use with multi-repository support")
        print("  2. Start the backend: cd ../backend && uvicorn app.main:app")
        print("  3. Start the frontend: cd ../frontend && npm start")
        print("  4. Open browser: http://localhost:3000")

        print("\n💡 Adding a new repository:")
        print("  1. Edit repositories.yaml")
        print("  2. Add your new repository configuration")
        print("  3. Re-run this training script")
        print("  4. New repo will be automatically included!")


def main():
    parser = argparse.ArgumentParser(
        description="Train ML models for multi-repository config management"
    )
    parser.add_argument(
        '--repos-config',
        default='../repositories.yaml',
        help='Path to repositories.yaml (default: ../repositories.yaml)'
    )

    args = parser.parse_args()

    trainer = MultiRepoConfigTrainer(args.repos_config)

    try:
        trainer.train()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Fix:")
        print("  1. Create repositories.yaml in project root")
        print("  2. Configure your repository paths")
        print("  3. Run: python train_models_multi_repo.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
