#!/usr/bin/env python3
"""
ML Model Training Script

This script trains machine learning models for configuration anomaly detection.
Run this once to train models, then deploy the trained models with the application.
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

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class ConfigTrainer:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize trainer with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.yaml_path = self.config['data']['yaml_files_path']
        self.file_pattern = self.config['data']['file_pattern']
        self.output_path = Path(self.config['models']['output_path'])
        self.output_path.mkdir(parents=True, exist_ok=True)

    def load_yaml_files(self) -> Dict[str, Any]:
        """Load all YAML configuration files"""
        yaml_files = {}
        yaml_dir = Path(self.yaml_path)

        if not yaml_dir.exists():
            raise FileNotFoundError(f"YAML directory not found: {self.yaml_path}")

        pattern = self.file_pattern.replace("*", "")
        for file_path in yaml_dir.glob(self.file_pattern):
            try:
                with open(file_path, 'r') as f:
                    content = yaml.safe_load(f)
                    yaml_files[file_path.name] = content
                    print(f"  ✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {e}")

        print(f"\n✅ Loaded {len(yaml_files)} YAML files")
        return yaml_files

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

    def extract_features(self, yaml_files: Dict[str, Any]) -> pd.DataFrame:
        """Extract features from YAML files for ML training"""
        print("\n📊 Extracting features...")

        # Get all unique keys across all files
        all_keys = set()
        flattened_configs = {}

        for filename, content in yaml_files.items():
            if content:
                flattened = self.flatten_dict(content)
                flattened_configs[filename] = flattened
                all_keys.update(flattened.keys())

        all_keys = sorted(list(all_keys))
        print(f"  ✓ Found {len(all_keys)} unique keys")

        # Create feature matrix: rows = files, columns = keys (binary: present/absent)
        feature_matrix = []
        file_names = []

        for filename, flattened in flattened_configs.items():
            features = [1 if key in flattened else 0 for key in all_keys]
            feature_matrix.append(features)
            file_names.append(filename)

        df = pd.DataFrame(feature_matrix, columns=all_keys, index=file_names)
        print(f"  ✓ Created feature matrix: {df.shape[0]} files × {df.shape[1]} features")

        return df, all_keys

    def train_isolation_forest(self, X: np.ndarray) -> IsolationForest:
        """Train Isolation Forest for anomaly detection"""
        print("\n🌲 Training Isolation Forest...")

        config = self.config['models']['isolation_forest']
        model = IsolationForest(
            contamination=config['contamination'],
            n_estimators=config['n_estimators'],
            random_state=config['random_state']
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

        config = self.config['models']['kmeans']
        model = KMeans(
            n_clusters=config['n_clusters'],
            random_state=config['random_state'],
            max_iter=config['max_iter']
        )

        model.fit(X)

        print(f"  ✓ Model trained successfully")
        print(f"  ✓ Created {config['n_clusters']} clusters")

        return model

    def save_models(self, isolation_forest, kmeans, feature_names: List[str],
                    file_names: List[str]):
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

        # Save model info
        model_info = {
            "trained_date": datetime.now().isoformat(),
            "num_environments": len(file_names),
            "num_features": len(feature_names),
            "version": "1.0.0",
            "trained_on_files": file_names,
            "isolation_forest_params": self.config['models']['isolation_forest'],
            "kmeans_params": self.config['models']['kmeans']
        }

        info_path = self.output_path / "model_info.json"
        with open(info_path, 'w') as f:
            json.dump(model_info, f, indent=2)
        print(f"  ✓ Saved: {info_path}")

    def train(self):
        """Main training pipeline"""
        print("=" * 60)
        print("🤖 ML Model Training Pipeline")
        print("=" * 60)

        # Load YAML files
        print("\n📂 Loading YAML files...")
        yaml_files = self.load_yaml_files()

        if len(yaml_files) < 3:
            print("⚠️  Warning: Less than 3 files found. Need more data for accurate training.")
            print("   Training will continue but results may not be optimal.")

        # Extract features
        df, feature_names = self.extract_features(yaml_files)
        X = df.values

        # Train models
        isolation_forest = self.train_isolation_forest(X)
        kmeans = self.train_kmeans(X)

        # Save everything
        self.save_models(isolation_forest, kmeans, feature_names, df.index.tolist())

        print("\n" + "=" * 60)
        print("✅ Training Complete!")
        print("=" * 60)
        print(f"\nModels saved to: {self.output_path.absolute()}")
        print("\nNext steps:")
        print("  1. Models are ready to use")
        print("  2. Start the backend: cd ../backend && uvicorn app.main:app")
        print("  3. Start the frontend: cd ../frontend && npm start")
        print("  4. Open browser: http://localhost:3000")
        print("\n💡 Tip: You only need to retrain when you add many new configs")


def main():
    parser = argparse.ArgumentParser(description="Train ML models for config management")
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config.yaml (default: config.yaml)'
    )
    parser.add_argument(
        '--data-path',
        help='Override YAML files path from config'
    )

    args = parser.parse_args()

    trainer = ConfigTrainer(args.config)

    # Override data path if provided
    if args.data_path:
        trainer.yaml_path = args.data_path
        print(f"Using YAML path: {args.data_path}")

    try:
        trainer.train()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Fix:")
        print("  1. Edit ml-training/config.yaml")
        print("  2. Set 'yaml_files_path' to your configs directory")
        print("  3. Or run: python train_models.py --data-path /path/to/configs")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
