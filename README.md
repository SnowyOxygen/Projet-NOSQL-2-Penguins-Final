# 🐧 Penguins Analysis Platform - Multi-NoSQL Database Benchmark

A comprehensive data analysis platform for penguin species classification using multiple NoSQL databases (MongoDB, Cassandra, Redis) with statistical analysis, visualization, regression modeling, and machine learning-based classification.

## 📋 Project Overview

This project implements a full-stack application that analyzes the Palmer Penguins dataset (LTER) across four analytical phases:

- **Part 1**: Descriptive Statistical Analysis
- **Part 2**: Data Visualization (distributions, correlations)
- **Part 3**: Simple & Multiple Linear Regression
- **Part 4**: Classification & Species Prediction (Random Forest)

## 🏗️ Architecture

```
penguins-analysis/
├── docker-compose.yml          # 6 microservices (3 DBs + API + Frontend + Init)
├── backend/                    # FastAPI Python backend
│   ├── app.py                  # Main FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection services
│   ├── schemas.py              # Pydantic models
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Backend container
│   ├── routers/                # API endpoint handlers
│   │   ├── health.py           # Health check
│   │   ├── part1.py            # Descriptive statistics
│   │   ├── part2.py            # Visualization data
│   │   ├── part3.py            # Regression analysis
│   │   └── part4.py            # Classification & prediction
│   └── services/
│       └── analysis.py         # Analysis & ML logic
├── frontend/                   # React TypeScript frontend
│   ├── package.json            # Node dependencies
│   ├── Dockerfile              # Frontend container
│   ├── public/index.html       # Main HTML file
│   └── src/
│       ├── index.js            # React entry point
│       ├── App.js              # Main React component
│       ├── App.css             # Main styles
│       └── components/         # React components (Part 1-4)
├── data/
│   ├── penguins_lter.csv       # Dataset
│   └── init_scripts/           # Database initialization
│       ├── init.py             # CSV data loader
│       ├── mongo-init.js       # MongoDB setup
│       └── cassandra-init.cql  # Cassandra setup
└── Dockerfile.init             # Database initialization container
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- At least 8GB RAM available
- Windows/macOS/Linux

### Running the Application

1. **Clone and navigate to project**:
   ```bash
   cd "SDV 2025\Projet NOSQL 2"
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Wait for initialization** (2-3 minutes):
   - MongoDB starts
   - Cassandra starts
   - Redis starts
   - Database initialization loads penguins_lter.csv
   - FastAPI backend initializes
   - React frontend builds and starts

4. **Access the application**:
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - API: http://localhost:8000

5. **Stop services**:
   ```bash
   docker-compose down
   ```

## 📊 Database Configuration

### MongoDB
- **Port**: 27017
- **Database**: `penguins`
- **Collection**: `penguins`
- **Data**: All 344 penguin records
- **Purpose**: Document storage, flexible schema

### Cassandra
- **Port**: 9042
- **Keyspace**: `penguins`
- **Table**: `penguins` (partitioned by species)
- **Data**: All 344 penguin records
- **Purpose**: Column-family distributed storage, time-series oriented

### Redis
- **Port**: 6379
- **Data Structure**: Hashes + Sets
- **Data**: All 344 penguin records cached
- **Purpose**: In-memory cache and session storage

## 🔌 API Endpoints

### Health Check
- `GET /api/health` - Check all database connections

### Part 1: Descriptive Statistics
- `GET /api/part1/summary` - Overall statistics
- `GET /api/part1/numeric-stats` - Summary statistics for numeric variables
- `GET /api/part1/species` - Species distribution

### Part 2: Visualization
- `GET /api/part2/distribution?variable={var}` - Distribution data for a variable
- `GET /api/part2/correlation` - Correlation matrix for all numeric variables

### Part 3: Regression
- `GET /api/part3/simple?predictor={var}` - Simple linear regression
- `POST /api/part3/multiple` - Multiple linear regression
  ```json
  {
    "predictors": ["bill_length_mm", "flipper_length_mm"],
    "target": "body_mass_g"
  }
  ```

### Part 4: Classification & Prediction
- `GET /api/part4/model-info` - Classification model metrics and feature importance
- `POST /api/part4/predict` - Predict species
  ```json
  {
    "bill_length_mm": 40.0,
    "bill_depth_mm": 18.0,
    "flipper_length_mm": 190,
    "body_mass_g": 3800
  }
  ```

## 📈 Features

### Part 1: Descriptive Analysis
- Total penguin count and dataset overview
- Numeric statistics (mean, median, min, max, std dev, variance)
- Missing value detection
- Species, island, and sex distribution
- Count summaries by categorical variables

### Part 2: Visualization
- Distribution histograms for each numeric variable
- Quartile analysis (Q0-Q4)
- Correlation matrix (heatmap)
- Interactive variable selector

### Part 3: Regression
- Simple linear regression with one predictor
- Multiple linear regression (2-3 predictors)
- Model metrics:
  - R² score (goodness of fit)
  - P-values (statistical significance)
  - Regression equations
  - Residual standard deviation
  - Number of samples used
- Target variable: Body Mass (g)
- Predictors: Bill length/depth, Flipper length

### Part 4: Classification & Prediction
- Random Forest classifier (100 trees)
- Real-time species prediction with input sliders
- Class probabilities for each species
- Confidence scores
- Model metrics:
  - Overall accuracy
  - Per-class precision, recall, F1-score
  - Confusion matrix
- Feature importance ranking
- Trained on 333 complete samples

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn
- **Python**: 3.11
- **Key Libraries**:
  - pymongo (MongoDB)
  - cassandra-driver (Cassandra)
  - redis (Redis)
  - pandas, numpy (Data processing)
  - scikit-learn (ML models)
  - scipy (Statistics)

### Frontend
- **Framework**: React 18.2
- **Build Tool**: Create React App
- **HTTP Client**: Axios
- **Styling**: CSS3

### Databases
- **MongoDB** 7.0 (Document)
- **Cassandra** 4.1 (Column-Family)
- **Redis** 7.2 (In-Memory)

## 📊 Dataset

**Palmer Penguins LTER** - 344 observations of penguin species from Antarctica

**Features**:
- `species`: Adelie, Chinstrap, Gentoo
- `island`: Torgersen, Biscoe, Dream
- `bill_length_mm`: 34.4 - 59.6 mm
- `bill_depth_mm`: 15.5 - 21.5 mm
- `flipper_length_mm`: 172 - 231 mm
- `body_mass_g`: 2700 - 6300 g
- `sex`: MALE, FEMALE, or missing
- `year`: 2007 - 2009

**Missing Values**:
- Some records have missing sex or isotope data
- Clean records (complete morphological data): 333

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Sample API Calls
```bash
# Get statistics
curl http://localhost:8000/api/part1/summary

# Get correlation matrix
curl http://localhost:8000/api/part2/correlation

# Simple regression
curl http://localhost:8000/api/part3/simple?predictor=flipper_length_mm

# Predict species
curl -X POST http://localhost:8000/api/part4/predict \
  -H "Content-Type: application/json" \
  -d '{"bill_length_mm":40, "bill_depth_mm":18, "flipper_length_mm":190, "body_mass_g":3800}'
```

## 🗂️ Project Structure Details

### Backend Services
- **health.py**: Database connection health checks
- **part1.py**: Exploratory data analysis endpoints
- **part2.py**: Descriptive stats for visualization
- **part3.py**: Regression model computation
- **part4.py**: Classification predictions and model metrics
- **analysis.py**: Statistical and ML computation logic

### Frontend Components
- **Part1.js**: Statistics tables and distributions
- **Part2.js**: Variable selection and correlation heatmap
- **Part3.js**: Regression model configuration and results
- **Part4.js**: Species prediction with sliders and model metrics

## 📝 Configuration

### Environment Variables
Located in `docker-compose.yml`:
- `MONGO_URL`: MongoDB connection string
- `CASSANDRA_HOST`: Cassandra hostname
- `REDIS_HOST`: Redis hostname
- `REACT_APP_API_URL`: API base URL

### Dataset Initialization
The `Dockerfile.init` service:
1. Waits for all 3 databases to be healthy
2. Parses `penguins_lter.csv`
3. Normalizes species names
4. Inserts records into MongoDB, Cassandra, and Redis
5. Completes and exits successfully
6. API and Frontend depend on this service completing

## 📚 Key Analytical Insights

### Exploratory Questions Addressed
1. **Which species are overrepresented?** - Adelie (152), Chinstrap (68), Gentoo (124)
2. **Marked size differences?** - Yes, Gentoo significantly larger than others
3. **Most discriminant variables?** - Flipper length and body mass highly correlated with species
4. **Strongest correlations?** - Flipper length & body mass (0.87), Body mass & bill length (0.60)
5. **Body mass predictors?** - Flipper length is strongest single predictor (R² ≈ 0.76)
6. **Hardest species to predict?** - Adelie and Chinstrap show some overlap
7. **Model accuracy?** - Random Forest achieves >97% accuracy

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port (e.g., 3000)
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000   # Windows
```

### Database Connection Errors
```bash
# Check service health
docker-compose ps
docker-compose logs api
```

### React Build Issues
```bash
# Clear cache and rebuild
docker-compose down
docker system prune -a
docker-compose up -d
```

## 📄 License

This project is part of the SDV 2025 curriculum - Projet NOSQL 2

## 👨‍💻 Development

### Adding New Variables
1. Add to CSV parsing in `data/init_scripts/init.py`
2. Update database schemas
3. Update Pydantic models in `backend/schemas.py`
4. Create new analysis functions in `backend/services/analysis.py`
5. Create API endpoints in `backend/routers/`
6. Add React components as needed

### Extending Analysis
- Modify `services/analysis.py` for new statistical methods
- Add new routers under `routers/` directory
- Create corresponding React components with styling

## 📞 Support

For issues or questions:
1. Check `docker-compose logs <service>` for errors
2. Verify all services started: `docker-compose ps`
3. Check API docs at http://localhost:8000/docs
4. Review console output in React app (F12)

---

**Penguins Analysis Platform v1.0** | Multi-NoSQL Benchmark | FastAPI + React
