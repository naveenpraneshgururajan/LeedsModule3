# Configuration Manager

Intelligent environment configuration management system with ML-based anomaly detection and automated uplift recommendations.

## 🎯 Features

- **ML-Powered Anomaly Detection** - Automatically detect missing keys and configuration drift
- **Smart Uplift Assistant** - Get intelligent recommendations for uplifting configs between environments
- **Change Tracking** - Track configuration changes over time using git history
- **Interactive UI** - Beautiful React + Material-UI interface
- **Environment Comparison** - Side-by-side config comparison
- **Coverage Reports** - Comprehensive coverage analysis across all environments
- **No Training Required** - Pre-trained models work immediately after deployment

## 📁 Project Structure

```
LeedsModule3/
├── ml-training/          # ML model training (run once)
│   ├── train_models.py   # Training script
│   ├── config.yaml       # Training configuration
│   └── README.md         # Training documentation
│
├── backend/              # FastAPI Backend
│   ├── app/             # FastAPI application
│   ├── core/            # Business logic (NO training code)
│   ├── models/          # Pre-trained ML models
│   └── requirements.txt
│
└── frontend/            # React + Material-UI Frontend
    ├── src/
    │   ├── components/  # React components
    │   ├── pages/       # Page components
    │   ├── hooks/       # Custom hooks
    │   ├── services/    # API client
    │   └── theme/       # Material-UI theme
    ├── webpack.config.js
    └── package.json
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- Your YAML configuration files

### Step 1: Train ML Models (One-Time)

```bash
cd ml-training

# Install dependencies
pip install -r requirements.txt

# Edit config.yaml and set your YAML files path
nano config.yaml  # Change yaml_files_path

# Train models
python train_models.py

# Models are saved to ../backend/models/
```

### Step 2: Setup Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Edit .env and set your paths
nano .env
# Set:
# YAML_FILES_PATH=/path/to/your/configs
# GIT_REPO_PATH=/path/to/your/configs

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at: `http://localhost:8000`

### Step 3: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be running at: `http://localhost:3000`

## 📖 Usage

### Dashboard

- View overall environment health
- See summary statistics
- Monitor recent changes

### Environments

- Browse all environments
- Filter by type (dev/cit/sit/luat/prod)
- View coverage and health status
- See missing keys

### Uplift Assistant

1. Select source environment (e.g., dev01)
2. Select target environment (e.g., cit01)
3. Click "Analyze Changes"
4. Review categorized recommendations:
   - 🔴 **Critical** - Must be uplifted
   - 🟡 **Recommended** - Should be uplifted
   - 🟢 **Optional** - May not need uplift
5. Generate checklist for implementation

### Reports

- View ML model status
- See detected anomalies
- Generate coverage reports
- Export to HTML/JSON

### Settings

- Configure file paths
- Adjust ML thresholds
- View system information

## 🔧 Configuration

### Backend Configuration (`.env`)

```bash
# Path to your YAML configuration files
YAML_FILES_PATH=/path/to/your/configs

# Git repository path (usually same as above)
GIT_REPO_PATH=/path/to/your/configs

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# ML Settings
ANOMALY_THRESHOLD=0.7
DEV_LENIENCY=0.5
```

### Frontend Configuration (`.env`)

```bash
REACT_APP_API_URL=http://localhost:8000
```

## 🤖 ML Models

### Training

Models are trained **once** using the `ml-training/` module:

```bash
cd ml-training
python train_models.py --data-path /path/to/your/configs
```

### Models Created

1. **Isolation Forest** (`isolation_forest.pkl`) - Anomaly detection
2. **KMeans** (`kmeans_clusters.pkl`) - Environment clustering
3. **Feature Names** (`feature_names.json`) - Configuration keys
4. **Model Info** (`model_info.json`) - Training metadata

### When to Retrain

- ✅ Added many new environment files (10+)
- ✅ Configuration structure changed significantly
- ✅ Want to improve accuracy
- ✅ Monthly/quarterly refresh

❌ **NOT needed for:**
- Deployment to new server
- Sharing with team members
- Minor config changes
- Testing/development

## 📤 Sharing with Team

### Option 1: Shared Folder

```bash
# Copy entire project folder
cp -r LeedsModule3 /shared/drive/

# Team members run:
cd LeedsModule3/backend && pip install -r requirements.txt
cd LeedsModule3/frontend && npm install
```

### Option 2: Git Repository

```bash
# Push to internal git server
git add .
git commit -m "Add config manager with pre-trained models"
git push

# Team members clone:
git clone your-repo
cd LeedsModule3
# Follow setup steps above
```

### Option 3: Zip File

```bash
zip -r config-manager.zip LeedsModule3 -x "*/node_modules/*" -x "*/__pycache__/*"
# Send config-manager.zip to colleagues
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn app.main:app --reload

# API documentation available at:
# http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend

# Development server
npm start

# Build for production
npm run build
```

## 📊 API Endpoints

### Environments
- `GET /api/environments` - Get all environments
- `GET /api/environments/{env_name}` - Get specific environment
- `GET /api/environments/{env_name}/compare/{target_env}` - Compare two environments

### Uplift
- `POST /api/uplift/analyze` - Analyze uplift requirements
- `POST /api/uplift/checklist` - Generate uplift checklist
- `GET /api/uplift/suggestions/{env_name}` - Get uplift suggestions

### Changes
- `GET /api/changes` - Get change history
- `GET /api/changes/recent` - Get recent changes
- `GET /api/changes/history/{env_name}` - Get environment history

### Reports
- `GET /api/reports/coverage` - Coverage report
- `GET /api/reports/anomalies` - Anomalies report
- `GET /api/reports/ml-status` - ML model status
- `GET /api/reports/summary` - Dashboard summary

Full API documentation: `http://localhost:8000/docs`

## 🧪 Troubleshooting

### Models Not Loading

```bash
# Check if models exist
ls -la backend/models/

# If missing, train models:
cd ml-training
python train_models.py
```

### Git Not Working

```bash
# Check git status
cd /path/to/your/configs
git status

# If not a git repo, initialize:
git init
git add .
git commit -m "Initial commit"
```

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r backend/requirements.txt

# Check .env file
cat backend/.env
```

### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf frontend/node_modules
cd frontend && npm install
```

## 🎨 Tech Stack

- **Backend**: FastAPI, scikit-learn, GitPython, PyYAML
- **Frontend**: React, TypeScript, Material-UI, React Query, Axios
- **Build**: Webpack
- **ML**: Isolation Forest, KMeans Clustering

## 📝 License

Internal use only.

## 🤝 Support

For issues or questions, contact the development team.

---

**Version**: 1.0.0
**Last Updated**: January 2026
