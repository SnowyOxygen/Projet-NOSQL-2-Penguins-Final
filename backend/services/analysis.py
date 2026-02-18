"""
Analysis services for Parts 1-4
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from scipy import stats
import logging
import joblib
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)
MODELS_DIR = Path(__file__).parent.parent / "models"

class AnalysisService:
    """Service for data analysis and statistics"""
    
    def __init__(self):
        self.df = None
        # Classifiers
        self.classifier_rf = None  # Random Forest
        self.classifier_knn = None  # K-NN
        self.classifier_dt = None  # Decision Tree
        self.label_encoders = {}
        self.feature_scaler = None
        # Model metadata
        self.model_metadata = {
            'rf': {'samples': None, 'date': None},
            'knn': {'samples': None, 'date': None},
            'dt': {'samples': None, 'date': None}
        }
        # Create models directory if it doesn't exist
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        # Load classifiers if they exist
        self._load_classifiers()
    
    def _load_classifier(self):
        """Load classifier from disk if available"""
        classifier_path = MODELS_DIR / "classifier.pkl"
        if classifier_path.exists():
            try:
                self.classifier_rf = joblib.load(classifier_path)
                logger.info("Loaded classifier from disk")
                # Load metadata
                self._load_model_metadata()
            except Exception as e:
                logger.error(f"Failed to load classifier: {e}")
                self.classifier_rf = None
    
    def _load_classifiers(self):
        """Load all classifiers from disk if available"""
        models = {
            'rf': ('classifier_rf', 'rf_classifier.pkl'),
            'knn': ('classifier_knn', 'knn_classifier.pkl'),
            'dt': ('classifier_dt', 'dt_classifier.pkl')
        }
        
        for model_key, (attr_name, filename) in models.items():
            classifier_path = MODELS_DIR / filename
            if classifier_path.exists():
                try:
                    classifier = joblib.load(classifier_path)
                    setattr(self, attr_name, classifier)
                    logger.info(f"Loaded {model_key.upper()} classifier from disk")
                except Exception as e:
                    logger.error(f"Failed to load {model_key.upper()} classifier: {e}")
        
        # Load metadata for all models
        self._load_all_model_metadata()
    
    def _load_model_metadata(self):
        """Load model metadata from disk"""
        metadata_path = MODELS_DIR / "model_metadata.txt"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        self.model_metadata['rf']['samples'] = int(lines[0].strip().split(': ')[1])
                        self.model_metadata['rf']['date'] = lines[1].strip().split(': ', 1)[1]
            except Exception as e:
                logger.error(f"Failed to load model metadata: {e}")
    
    def _load_all_model_metadata(self):
        """Load metadata for all models from disk"""
        for model_key in ['rf', 'knn', 'dt']:
            metadata_path = MODELS_DIR / f"{model_key}_metadata.txt"
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r') as f:
                        lines = f.readlines()
                        if len(lines) >= 2:
                            self.model_metadata[model_key]['samples'] = int(lines[0].strip().split(': ')[1])
                            self.model_metadata[model_key]['date'] = lines[1].strip().split(': ', 1)[1]
                except Exception as e:
                    logger.error(f"Failed to load {model_key.upper()} metadata: {e}")
    
    def _save_model_metadata(self, samples: int):
        """Save model metadata to disk"""
        try:
            metadata_path = MODELS_DIR / "model_metadata.txt"
            with open(metadata_path, 'w') as f:
                f.write(f"samples: {samples}\n")
                f.write(f"trained_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.model_metadata['rf']['samples'] = samples
            self.model_metadata['rf']['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.error(f"Failed to save model metadata: {e}")
    
    def _save_classifier(self):
        """Save classifier to disk"""
        try:
            classifier_path = MODELS_DIR / "classifier.pkl"
            joblib.dump(self.classifier_rf, classifier_path)
            logger.info("Saved classifier to disk")
        except Exception as e:
            logger.error(f"Failed to save classifier: {e}")
    
    def _save_all_models(self, model_key: str, classifier, samples: int):
        """Save classifier and metadata to disk"""
        try:
            filename_map = {'rf': 'rf_classifier.pkl', 'knn': 'knn_classifier.pkl', 'dt': 'dt_classifier.pkl'}
            classifier_path = MODELS_DIR / filename_map[model_key]
            joblib.dump(classifier, classifier_path)
            logger.info(f"Saved {model_key.upper()} classifier to disk")
            
            # Save metadata
            metadata_path = MODELS_DIR / f"{model_key}_metadata.txt"
            with open(metadata_path, 'w') as f:
                f.write(f"samples: {samples}\n")
                f.write(f"trained_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.model_metadata[model_key]['samples'] = samples
            self.model_metadata[model_key]['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.error(f"Failed to save {model_key.upper()} model and metadata: {e}")
    
    def load_data(self, penguins: List[Dict]):
        """Load penguin data into pandas DataFrame"""
        self.df = pd.DataFrame(penguins)
        # Clean species names
        self.df['species'] = self.df['species'].str.strip()
        logger.info(f"Loaded {len(self.df)} penguins")
    
    # PART 1: DESCRIPTIVE STATISTICS
    def get_part1_summary(self) -> Dict[str, Any]:
        """Get descriptive statistics for Part 1"""
        numeric_cols = ['culmenLength', 'culmenDepth', 'flipperLength', 'bodyMass']
        
        # Calculate stats for numeric columns
        numeric_stats = []
        for col in numeric_cols:
            col_data = pd.to_numeric(self.df[col], errors='coerce')
            numeric_stats.append({
                'variable': col,
                'mean': float(col_data.mean()) if col_data.notna().sum() > 0 else None,
                'median': float(col_data.median()) if col_data.notna().sum() > 0 else None,
                'min': float(col_data.min()) if col_data.notna().sum() > 0 else None,
                'max': float(col_data.max()) if col_data.notna().sum() > 0 else None,
                'std': float(col_data.std()) if col_data.notna().sum() > 0 else None,
                'count': int(col_data.notna().sum()),
                'missing_count': int(col_data.isna().sum())
            })
        
        # Missing values
        missing_values = {}
        for col in self.df.columns:
            missing_count = int(self.df[col].isna().sum())
            if missing_count > 0:
                missing_values[col] = missing_count
        
        # Species counts
        species_counts = []
        for species, count in self.df['species'].value_counts().items():
            species_counts.append({'species': species, 'count': int(count)})
        
        # Island counts
        island_counts = []
        for island, count in self.df['island'].value_counts().items():
            island_counts.append({'island': island, 'count': int(count)})
        
        # Sex counts - group non-MALE/FEMALE values as "incorrect"
        sex_counts = []
        male_count = 0
        female_count = 0
        incorrect_count = 0
        
        for sex, count in self.df['sex'].value_counts(dropna=False).items():
            sex_upper = str(sex).upper() if pd.notna(sex) else ''
            if sex_upper == 'MALE':
                male_count += count
            elif sex_upper == 'FEMALE':
                female_count += count
            else:
                incorrect_count += count
        
        if male_count > 0:
            sex_counts.append({'sex': 'MALE', 'count': int(male_count)})
        if female_count > 0:
            sex_counts.append({'sex': 'FEMALE', 'count': int(female_count)})
        if incorrect_count > 0:
            sex_counts.append({'sex': 'incorrect', 'count': int(incorrect_count)})
        
        return {
            'total_penguins': len(self.df),
            'missing_values': missing_values,
            'numeric_stats': numeric_stats,
            'species_counts': species_counts,
            'island_counts': island_counts,
            'sex_counts': sex_counts
        }
    
    # PART 2: VISUALIZATION
    def get_distribution_data(self, variable: str, bins: int = 10) -> Dict[str, Any]:
        """Get distribution data for a variable"""
        col_map = {
            'bill_length_mm': 'culmenLength',
            'bill_depth_mm': 'culmenDepth',
            'flipper_length_mm': 'flipperLength',
            'body_mass_g': 'bodyMass'
        }
        col = col_map.get(variable, variable)
        
        if col not in self.df.columns:
            raise ValueError(f"Unknown variable: {variable}")
        
        col_data = pd.to_numeric(self.df[col], errors='coerce').dropna()
        
        # Histogram
        counts, bin_edges = np.histogram(col_data, bins=bins)
        histogram = []
        for i, count in enumerate(counts):
            bin_label = f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}"
            histogram.append({'bin': bin_label, 'count': int(count)})
        
        # Quartiles
        quartiles = {
            'q0': float(col_data.min()),
            'q1': float(col_data.quantile(0.25)),
            'q2': float(col_data.quantile(0.5)),
            'q3': float(col_data.quantile(0.75)),
            'q4': float(col_data.max())
        }
        
        return {
            'variable': variable,
            'histogram': histogram,
            'quartiles': quartiles,
            'count': len(col_data),
            'mean': float(col_data.mean()),
            'std': float(col_data.std())
        }
    
    def get_correlation_matrix(self) -> Dict[str, Any]:
        """Get correlation matrix for numeric variables"""
        numeric_cols = ['culmenLength', 'culmenDepth', 'flipperLength', 'bodyMass']
        cor_df = self.df[numeric_cols].corr()
        
        variables = numeric_cols
        correlation_matrix = []
        for col in numeric_cols:
            row = []
            for col2 in numeric_cols:
                val = cor_df.loc[col, col2]
                row.append(float(val) if not pd.isna(val) else 0.0)
            correlation_matrix.append(row)
        
        return {
            'variables': variables,
            'correlations': correlation_matrix
        }
    
    def get_scatter_data(self) -> Dict[str, Any]:
        """Get scatter plot data for Part 2 analysis"""
        # Prepare data
        df_clean = self.df[['culmenLength', 'culmenDepth', 'flipperLength', 'bodyMass', 'species', 'sex']].copy()
        df_clean = df_clean.dropna(subset=['culmenLength', 'culmenDepth', 'flipperLength', 'bodyMass'])
        
        # Scatter 1: Bill length vs depth by species
        bill_scatter = []
        for species in df_clean['species'].unique():
            species_data = df_clean[df_clean['species'] == species]
            for _, row in species_data.iterrows():
                bill_scatter.append({
                    'x': float(row['culmenLength']),
                    'y': float(row['culmenDepth']),
                    'species': species
                })
        
        # Scatter 2: Flipper length vs body mass by sex
        flipper_scatter = []
        for sex in df_clean['sex'].unique():
            if pd.notna(sex) and str(sex).upper() in ['MALE', 'FEMALE']:
                sex_data = df_clean[df_clean['sex'] == sex]
                for _, row in sex_data.iterrows():
                    flipper_scatter.append({
                        'x': float(row['flipperLength']),
                        'y': float(row['bodyMass']),
                        'sex': str(sex).upper()
                    })
        
        return {
            'bill_scatter': bill_scatter,
            'flipper_scatter': flipper_scatter
        }
    
    # PART 3: REGRESSION
    def simple_regression(self, predictor: str, target: str = 'bodyMass') -> Dict[str, Any]:
        """Perform simple linear regression"""
        col_map = {
            'bill_length_mm': 'culmenLength',
            'bill_depth_mm': 'culmenDepth',
            'flipper_length_mm': 'flipperLength',
            'body_mass_g': 'bodyMass'
        }
        
        pred_col = col_map.get(predictor, predictor)
        tgt_col = col_map.get(target, target)
        
        # Clean data
        data = self.df[[pred_col, tgt_col]].dropna()
        if len(data) == 0:
            raise ValueError("No valid data for regression")
        
        x = data[pred_col].values.reshape(-1, 1)
        y = data[tgt_col].values
        
        # Fit model
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(x, y)
        
        # Calculate metrics
        y_pred = model.predict(x)
        residuals = y - y_pred
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # P-value
        n = len(x)
        dof = n - 2
        t_stat = model.coef_[0] / (np.std(residuals) / np.sqrt(np.sum((x - x.mean()) ** 2)))
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), dof))
        
        return {
            'predictor': predictor,
            'target': target,
            'intercept': float(model.intercept_),
            'coefficient': float(model.coef_[0]),
            'r_squared': float(r_squared),
            'p_value': float(p_value),
            'equation': f"y = {model.intercept_:.2f} + {model.coef_[0]:.4f}*x",
            'residual_std': float(np.std(residuals)),
            'samples_used': len(data)
        }
    
    def multiple_regression(self, predictors: List[str], target: str = 'bodyMass') -> Dict[str, Any]:
        """Perform multiple linear regression"""
        col_map = {
            'bill_length_mm': 'culmenLength',
            'bill_depth_mm': 'culmenDepth',
            'flipper_length_mm': 'flipperLength',
            'body_mass_g': 'bodyMass'
        }
        
        pred_cols = [col_map.get(p, p) for p in predictors]
        tgt_col = col_map.get(target, target)
        
        # Clean data
        all_cols = pred_cols + [tgt_col]
        data = self.df[all_cols].dropna()
        if len(data) == 0:
            raise ValueError("No valid data for regression")
        
        x = data[pred_cols].values
        y = data[tgt_col].values
        
        # Fit model
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(x, y)
        
        # Calculate metrics
        y_pred = model.predict(x)
        residuals = y - y_pred
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # P-value
        n = len(x)
        dof = n - len(pred_cols) - 1
        f_stat = (ss_tot - ss_res) / (ss_res / dof)
        p_value = 1 - stats.f.cdf(f_stat, len(pred_cols), dof)
        
        coefficients = {pred: float(coef) for pred, coef in zip(predictors, model.coef_)}
        
        return {
            'predictors': predictors,
            'target': target,
            'intercept': float(model.intercept_),
            'coefficients': coefficients,
            'r_squared': float(r_squared),
            'p_value': float(p_value),
            'residual_std': float(np.std(residuals)),
            'samples_used': len(data)
        }
    
    # PART 4: CLASSIFICATION
    def train_classifier(self):
        """Train all classifiers (Random Forest, K-NN, Decision Tree)"""
        # Prepare data
        feature_cols = ['culmenLength', 'culmenDepth', 'flipperLength', 'bodyMass']
        data = self.df[feature_cols + ['species']].dropna()
        
        X = data[feature_cols].values
        y = data['species'].values
        n_samples = len(data)
        
        # Train Random Forest
        self.classifier_rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        self.classifier_rf.fit(X, y)
        self._save_all_models('rf', self.classifier_rf, n_samples)
        
        # Train K-NN
        self.classifier_knn = KNeighborsClassifier(n_neighbors=5)
        self.classifier_knn.fit(X, y)
        self._save_all_models('knn', self.classifier_knn, n_samples)
        
        # Train Decision Tree
        self.classifier_dt = DecisionTreeClassifier(random_state=42, max_depth=10)
        self.classifier_dt.fit(X, y)
        self._save_all_models('dt', self.classifier_dt, n_samples)
        
        logger.info(f"Trained all classifiers on {n_samples} samples")
    
    def predict_species(self, bill_length: float, bill_depth: float, flipper_length: float, body_mass: float) -> Dict[str, Any]:
        """Predict penguin species using Random Forest"""
        if self.classifier_rf is None:
            self.train_classifier()
        
        X = np.array([[bill_length, bill_depth, flipper_length, body_mass]])
        prediction = self.classifier_rf.predict(X)[0]
        probabilities = self.classifier_rf.predict_proba(X)[0]
        
        prob_dict = {}
        for i, species in enumerate(self.classifier_rf.classes_):
            prob_dict[species] = float(probabilities[i])
        
        return {
            'predicted_species': prediction,
            'probabilities': prob_dict,
            'confidence': float(max(probabilities))
        }
    
    def get_classification_metrics(self) -> Dict[str, Any]:
        """Get classification metrics for all models"""
        if self.classifier_rf is None:
            self.train_classifier()
        
        # Prepare data
        feature_cols = ['culmenLength', 'culmenDepth', 'flipperLength', 'bodyMass']
        data = self.df[feature_cols + ['species']].dropna()
        
        X = data[feature_cols].values
        y = data['species'].values
        
        metrics_dict = {}
        
        # Get metrics for each classifier
        for model_key, classifier in [('rf', self.classifier_rf), ('knn', self.classifier_knn), ('dt', self.classifier_dt)]:
            if classifier is None:
                continue
                
            y_pred = classifier.predict(X)
            
            accuracy = accuracy_score(y, y_pred)
            precision = precision_score(y, y_pred, average=None, labels=classifier.classes_, zero_division=0)
            recall = recall_score(y, y_pred, average=None, labels=classifier.classes_, zero_division=0)
            f1 = f1_score(y, y_pred, average=None, labels=classifier.classes_, zero_division=0)
            
            cm = confusion_matrix(y, y_pred, labels=classifier.classes_)
            
            metrics_dict[model_key] = {
                'accuracy': float(accuracy),
                'precision': {species: float(p) for species, p in zip(classifier.classes_, precision)},
                'recall': {species: float(r) for species, r in zip(classifier.classes_, recall)},
                'f1_score': {species: float(f) for species, f in zip(classifier.classes_, f1)},
                'confusion_matrix': {
                    'species': list(classifier.classes_),
                    'matrix': cm.tolist()
                }
            }
        
        return metrics_dict
    
    def get_feature_importances(self) -> Dict[str, Any]:
        """Get feature importances for all classifiers that support it"""
        if self.classifier_rf is None:
            self.train_classifier()
        
        feature_names = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
        importances_dict = {}
        
        # Random Forest
        if self.classifier_rf and hasattr(self.classifier_rf, 'feature_importances_'):
            importances_dict['rf'] = [
                {'feature': name, 'importance': float(imp)}
                for name, imp in zip(feature_names, self.classifier_rf.feature_importances_)
            ]
        
        # Decision Tree
        if self.classifier_dt and hasattr(self.classifier_dt, 'feature_importances_'):
            importances_dict['dt'] = [
                {'feature': name, 'importance': float(imp)}
                for name, imp in zip(feature_names, self.classifier_dt.feature_importances_)
            ]
        
        # K-NN doesn't have feature importances (non-tree based)
        importances_dict['knn'] = None
        
        return importances_dict
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model training statistics for all models"""
        models_info = {
            'rf': {
                'name': 'Random Forest',
                'description': '100 Estimators',
                'path': MODELS_DIR / 'rf_classifier.pkl',
                'exists': (MODELS_DIR / 'rf_classifier.pkl').exists()
            },
            'knn': {
                'name': 'K-Nearest Neighbors',
                'description': '5 Neighbors',
                'path': MODELS_DIR / 'knn_classifier.pkl',
                'exists': (MODELS_DIR / 'knn_classifier.pkl').exists()
            },
            'dt': {
                'name': 'Decision Tree',
                'description': 'Max Depth 10',
                'path': MODELS_DIR / 'dt_classifier.pkl',
                'exists': (MODELS_DIR / 'dt_classifier.pkl').exists()
            }
        }
        
        stats_dict = {}
        for model_key, info in models_info.items():
            stats_dict[model_key] = {
                'name': info['name'],
                'description': info['description'],
                'exists': info['exists'],
                'path': str(info['path']),
                'trained_samples': self.model_metadata[model_key]['samples'],
                'trained_date': self.model_metadata[model_key]['date']
            }
        
        return stats_dict

# Global service instance
analysis_service = AnalysisService()
