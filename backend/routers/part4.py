"""
Part 4: Classification and Prediction
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database import mongo_service
from services.analysis import analysis_service
import logging
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)
MODELS_DIR = Path(__file__).parent.parent / "models"

class PredictionInput(BaseModel):
    """Input for species prediction"""
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

@router.get("/model-info")
async def get_model_info():
    """Get classification model information for all models"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        # Get metrics for all models
        metrics = analysis_service.get_classification_metrics()
        
        # Get feature importances for all models
        feature_importances = analysis_service.get_feature_importances()
        
        trained_on_samples = len([p for p in penguins if p.get('culmenLength') and p.get('culmenDepth') and p.get('flipperLength') and p.get('bodyMass')])
        
        return {
            "model_type": "Multiple (Random Forest, K-NN, Decision Tree)",
            "metrics": metrics,
            "feature_importances": feature_importances,
            "trained_on_samples": trained_on_samples
        }
    except Exception as e:
        logger.error(f"Error in /model-info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict_species(data: PredictionInput):
    """Predict penguin species"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        prediction = analysis_service.predict_species(
            data.bill_length_mm,
            data.bill_depth_mm,
            data.flipper_length_mm,
            data.body_mass_g
        )
        return prediction
    except Exception as e:
        logger.error(f"Error in /predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_model_stats():
    """Get model training statistics and status"""
    try:
        stats = analysis_service.get_model_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in /stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
async def retrain_model():
    """Force retraining of the classifier and save it"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        # Force retraining
        analysis_service.train_classifier()
        
        return {
            "status": "success",
            "message": "Model retrained and saved successfully",
            "samples_trained": len([p for p in penguins if p.get('culmenLength') and p.get('culmenDepth') and p.get('flipperLength') and p.get('bodyMass')])
        }
    except Exception as e:
        logger.error(f"Error in /retrain: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/model")
async def delete_persisted_model(model: str = None):
    """Delete persisted model file(s)"""
    try:
        if model:
            # Delete specific model
            filename_map = {'rf': 'rf_classifier.pkl', 'knn': 'knn_classifier.pkl', 'dt': 'dt_classifier.pkl'}
            if model not in filename_map:
                raise HTTPException(status_code=400, detail=f"Invalid model: {model}")
            
            model_path = MODELS_DIR / filename_map[model]
            metadata_path = MODELS_DIR / f"{model}_metadata.txt"
            
            if model_path.exists():
                model_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Clear from memory
            if model == 'rf':
                analysis_service.classifier_rf = None
            elif model == 'knn':
                analysis_service.classifier_knn = None
            elif model == 'dt':
                analysis_service.classifier_dt = None
            
            return {
                "status": "success",
                "message": f"{model.upper()} model deleted successfully"
            }
        else:
            # Delete all models
            for model_key in ['rf', 'knn', 'dt']:
                filename_map = {'rf': 'rf_classifier.pkl', 'knn': 'knn_classifier.pkl', 'dt': 'dt_classifier.pkl'}
                model_path = MODELS_DIR / filename_map[model_key]
                metadata_path = MODELS_DIR / f"{model_key}_metadata.txt"
                
                if model_path.exists():
                    model_path.unlink()
                if metadata_path.exists():
                    metadata_path.unlink()
            
            # Clear from memory
            analysis_service.classifier_rf = None
            analysis_service.classifier_knn = None
            analysis_service.classifier_dt = None
            
            return {
                "status": "success",
                "message": "All models deleted successfully"
            }
    except Exception as e:
        logger.error(f"Error in /delete: {e}")
        raise HTTPException(status_code=500, detail=str(e))
