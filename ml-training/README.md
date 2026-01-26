# ML Training Module

This module trains machine learning models for configuration anomaly detection.

## Purpose

Train ML models **once** on your existing YAML configuration files. The trained models are then used by the main application to detect missing keys and anomalies.

## Quick Start

### 1. Install Dependencies

```bash
cd ml-training
pip install -r requirements.txt
```

### 2. Configure

Edit `config.yaml` and set your YAML files path:

```yaml
data:
  yaml_files_path: /path/to/your/configs  # <- Change this!
  file_pattern: "env-*.yaml"
```

### 3. Train Models

```bash
python train_models.py
```

Or specify path directly:

```bash
python train_models.py --data-path /path/to/your/configs
```

### 4. Output

Models are saved to `../backend/models/`:
- `isolation_forest.pkl` - Anomaly detection model
- `kmeans_clusters.pkl` - Environment clustering model
- `feature_names.json` - List of all configuration keys
- `model_info.json` - Training metadata

## When to Retrain

You typically **don't need to retrain** unless:

- ✅ You add many new environment files (10+)
- ✅ Configuration structure changes significantly
- ✅ You want to improve accuracy
- ✅ Monthly/quarterly refresh

## How It Works

1. **Loads** all your `env-*.yaml` files
2. **Extracts** all unique configuration keys
3. **Trains** Isolation Forest for anomaly detection
4. **Trains** KMeans for environment clustering
5. **Saves** models as `.pkl` files

## Models Explained

### Isolation Forest
- Detects configuration anomalies
- Identifies missing keys
- Flags unusual patterns
- Works even with new keys added

### KMeans Clustering
- Groups similar environments
- Helps identify which envs should have similar configs
- Compares dev/cit/sit/luat/prod patterns

## Troubleshooting

### Error: Directory not found
```
Fix: Edit config.yaml and set correct yaml_files_path
```

### Warning: Less than 3 files
```
Tip: Need at least 3 YAML files for meaningful training
Training will work but accuracy may be lower
```

### Models not loading in app
```
Fix: Make sure models/ directory is in backend/models/
Check that .pkl files exist
```

## Advanced Usage

### Custom configuration

```bash
python train_models.py --config my_config.yaml
```

### Different data path

```bash
python train_models.py --data-path /custom/path/to/yamls
```

## Next Steps

After training:

1. Models are automatically saved to `backend/models/`
2. Start the backend application
3. Models will load automatically
4. No retraining needed on deployment!

## File Structure

```
ml-training/
├── train_models.py      # Main training script
├── config.yaml          # Training configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```
