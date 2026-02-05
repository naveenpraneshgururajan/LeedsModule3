# Multi-Repository Configuration Guide

## 🎯 Overview

The Configuration Manager now supports **multiple repositories** with different folder structures. You can track configurations across:

- ✅ Multiple git repositories
- ✅ Different folder structures
- ✅ Multiple YAML files per environment
- ✅ Easy addition of new repositories

---

## 📁 Supported Repository Structures

### **Structure 1: Simple (Original)**
Files directly in repository root:
```
/path/to/configs/
├── env-dev01.yaml
├── env-dev02.yaml
├── env-cit01.yaml
└── env-cit02.yaml
```

### **Structure 2: Folder-Based (New)**
Environment folders with multiple YAML files:
```
/path/to/repo/src/env/
├── cit01/
│   ├── feature-switches.yaml
│   ├── adgroup.yaml
│   ├── dsapps/
│   │   ├── app1.yaml
│   │   └── app2.yaml
│   └── cwa/
│       └── config.yaml
├── cit02/
│   ├── feature-switches.yaml
│   └── adgroup.yaml
└── sit01/
    ├── feature-switches.yaml
    └── adgroup.yaml
```

---

## ⚙️ Configuration

### **1. Create `repositories.yaml`**

Create this file in the project root (`/home/user/LeedsModule3/repositories.yaml`):

```yaml
# Multi-Repository Configuration
repositories:
  # Your original simple structure
  - name: "main-configs"
    path: "/path/to/your/main/configs"
    enabled: true
    structure: "simple"
    file_pattern: "env-*.yaml"

  # Your new folder-based structure
  - name: "env-configs"
    path: "/path/to/your/env-configs/repo"
    enabled: true
    structure: "folder"
    base_path: "src/env"
    file_patterns:
      - "feature-switches.yaml"
      - "adgroup.yaml"
      - "dsapps/*.yaml"
      - "cwa/*.yaml"

  # Add more repositories here as needed
  - name: "legacy-configs"
    path: "/path/to/legacy/configs"
    enabled: false  # Disabled for now
    structure: "simple"
    file_pattern: "*.yaml"

environment_extraction:
  folder_pattern: "src/env/{env_name}"
  file_pattern: "env-{env_name}.yaml"

git:
  track_changes: true
  use_local_git: true

ml_training:
  aggregate_configs: true
  min_environments: 3
```

### **2. Update Paths**

Edit `repositories.yaml` and set actual paths:

```yaml
repositories:
  - name: "env-configs"
    path: "/actual/path/to/your/repo"  # <- Change this!
    enabled: true
    structure: "folder"
    base_path: "src/env"
```

---

## 🚀 Training Models with Multiple Repositories

### **Step 1: Install Dependencies**
```bash
cd ml-training
pip install -r requirements.txt
```

### **Step 2: Configure Repositories**
Edit `repositories.yaml` with your actual repository paths.

### **Step 3: Train Models**
```bash
cd ml-training
python train_models_multi_repo.py
```

**Output:**
```
🤖 ML Model Training Pipeline - Multi-Repository Support
======================================================================

📂 Repository Configuration:
   Total repositories: 2
   Enabled repositories: 2

   📁 main-configs:
      Path: /path/to/your/main/configs
      Structure: simple
      Environments: 6
      Names: dev01, dev02, dev03, dev04, dev06

   📁 env-configs:
      Path: /path/to/your/env-configs/repo
      Structure: folder
      Environments: 15
      Names: cit01, cit02, cit03, sit01, sit02

📂 Loading environments from all repositories...
✅ Total environments across all repos: 21

📊 Extracting features...
  ✓ Found 1,247 unique keys across all repos
  ✓ Created feature matrix: 21 environments × 1,247 features

🌲 Training Isolation Forest...
  ✓ Model trained successfully
  ✓ Detected 3 potential anomalies

🎯 Training KMeans Clustering...
  ✓ Model trained successfully
  ✓ Created 5 clusters

💾 Saving models...
  ✓ Saved: ../backend/models/isolation_forest.pkl
  ✓ Saved: ../backend/models/kmeans_clusters.pkl
  ✓ Saved: ../backend/models/feature_names.json
  ✓ Saved: ../backend/models/model_info.json

✅ Training Complete!
```

---

## 🔧 Using Multi-Repository Mode in Backend

### **Option 1: Auto-Detection (Recommended)**

The backend automatically detects if `repositories.yaml` exists:

```bash
cd backend
uvicorn app.main:app --reload
```

If `repositories.yaml` exists → **Multi-repo mode**
If not → **Single-repo mode** (backward compatible)

### **Option 2: Explicit Configuration**

Set environment variable:
```bash
export REPOS_CONFIG_PATH=/path/to/repositories.yaml
uvicorn app.main:app --reload
```

---

## ➕ Adding a New Repository

### **Step 1: Edit `repositories.yaml`**

```yaml
repositories:
  # Existing repos...

  # Add your new repository
  - name: "new-config-repo"
    path: "/path/to/new/repo"
    enabled: true
    structure: "folder"  # or "simple"
    base_path: "configs"
    file_patterns:
      - "*.yaml"
```

### **Step 2: Retrain Models**

```bash
cd ml-training
python train_models_multi_repo.py
```

### **Step 3: Restart Backend**

```bash
cd backend
# Restart uvicorn (Ctrl+C then run again)
uvicorn app.main:app --reload
```

**That's it!** The new repository is now tracked. ✅

---

## 📊 How It Works

### **Environment Aggregation**

For folder-based structures, all YAML files are aggregated:

```
cit01/
├── feature-switches.yaml    → Prefixed: feature-switches.*
├── adgroup.yaml             → Prefixed: adgroup.*
└── dsapps/
    └── app1.yaml            → Prefixed: app1.*
```

**Result:**
```python
{
  "feature-switches.feature1": "enabled",
  "feature-switches.feature2": "disabled",
  "adgroup.group1": "value",
  "app1.setting": "value"
}
```

### **Cross-Repository Comparison**

You can compare environments from **different repositories**:

```bash
# Compare cit01 from env-configs with dev01 from main-configs
GET /api/environments/cit01/compare/dev01
```

The system automatically handles the different structures!

---

## 🎯 API Endpoints (Multi-Repo)

All existing endpoints work the same way:

```bash
# Get all environments (from all repos)
GET /api/environments

# Get specific environment
GET /api/environments/cit01

# Compare environments (can be from different repos)
GET /api/environments/cit01/compare/dev01

# Uplift analysis
POST /api/uplift/analyze
{
  "source": "dev01",
  "target": "cit01"
}
```

**New endpoint:**
```bash
# Get repository summary
GET /api/repositories/summary

Response:
{
  "total_repos": 2,
  "enabled_repos": 2,
  "repositories": [
    {
      "name": "main-configs",
      "environment_count": 6,
      "environments": ["dev01", "dev02", ...]
    },
    {
      "name": "env-configs",
      "environment_count": 15,
      "environments": ["cit01", "cit02", ...]
    }
  ]
}
```

---

## 🔍 Example Use Cases

### **Use Case 1: Different Teams, Different Repos**

```yaml
repositories:
  - name: "team-a-configs"
    path: "/repos/team-a/configs"
    enabled: true
    structure: "simple"

  - name: "team-b-configs"
    path: "/repos/team-b/configs"
    enabled: true
    structure: "folder"
```

Track configs from both teams in one system!

### **Use Case 2: Migration**

```yaml
repositories:
  - name: "legacy-configs"
    path: "/old/configs"
    enabled: true
    structure: "simple"

  - name: "new-configs"
    path: "/new/configs"
    enabled: true
    structure: "folder"
```

Track both old and new structures during migration.

### **Use Case 3: Multiple Products**

```yaml
repositories:
  - name: "product-a"
    path: "/products/a/configs"
    enabled: true

  - name: "product-b"
    path: "/products/b/configs"
    enabled: true
```

Manage multiple product configurations centrally.

---

## ⚠️ Important Notes

### **File Patterns**

For folder structure, be specific with patterns:
```yaml
file_patterns:
  - "feature-switches.yaml"  # Exact filename
  - "*.yaml"                 # All YAML files
  - "dsapps/*.yaml"          # All YAML in dsapps folder
  - "**/*.yaml"              # All YAML recursively
```

### **Environment Naming**

- For **simple structure**: Name extracted from filename (`env-dev01.yaml` → `dev01`)
- For **folder structure**: Name is the folder name (`src/env/cit01/` → `cit01`)

### **Git Requirements**

Each repository should be a git repository for change tracking:
```bash
cd /path/to/your/repo
git init  # If not already a git repo
```

---

## 🐛 Troubleshooting

### **Error: "Repository path not found"**

**Fix:**
```bash
# Check path exists
ls -la /path/in/repositories.yaml

# Update repositories.yaml with correct path
```

### **Error: "No environments found"**

**Fix:**
```bash
# Check file patterns match your structure
ls /path/to/repo/src/env/*/feature-switches.yaml

# Update file_patterns in repositories.yaml
```

### **Error: "Models not loading"**

**Fix:**
```bash
# Retrain models with multi-repo
cd ml-training
python train_models_multi_repo.py

# Check models exist
ls -la backend/models/
```

---

## 📋 Quick Reference

| Task | Command |
|------|---------|
| **Configure repos** | Edit `repositories.yaml` |
| **Train models** | `python train_models_multi_repo.py` |
| **Add new repo** | Add to `repositories.yaml` + retrain |
| **Disable repo** | Set `enabled: false` in config |
| **Check status** | `GET /api/repositories/summary` |

---

## 🎉 Benefits

- ✅ **Centralized tracking** across multiple repos
- ✅ **Flexible structures** (simple or folder-based)
- ✅ **Easy to add** new repositories
- ✅ **Backward compatible** with single-repo mode
- ✅ **Cross-repo comparisons** and uplifts
- ✅ **No code changes** needed to add repos (just config)

---

## 📞 Need Help?

If you have issues:
1. Check `repositories.yaml` paths are correct
2. Verify file patterns match your structure
3. Run training with `python train_models_multi_repo.py --help`
4. Check backend logs for errors

Happy multi-repo tracking! 🚀
