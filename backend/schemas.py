"""
Pydantic models for API responses
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PenguinData(BaseModel):
    """Penguin data model"""
    studyName: str
    sampleNumber: int
    species: str
    region: str
    island: str
    stage: str
    individualId: str
    clutchCompletion: str
    dateEgg: str
    culmenLength: Optional[float] = None
    culmenDepth: Optional[float] = None
    flipperLength: Optional[int] = None
    bodyMass: Optional[int] = None
    sex: Optional[str] = None
    delta15N: Optional[float] = None
    delta13C: Optional[float] = None
    comments: Optional[str] = None

# Part 1 Models
class DescriptiveStats(BaseModel):
    """Descriptive statistics for a variable"""
    variable: str
    mean: Optional[float]
    median: Optional[float]
    min: Optional[float]
    max: Optional[float]
    std: Optional[float]
    count: int
    missing_count: int

class SpeciesCount(BaseModel):
    """Count of penguins by species"""
    species: str
    count: int

class IslandCount(BaseModel):
    """Count of penguins by island"""
    island: str
    count: int

class SexCount(BaseModel):
    """Count of penguins by sex"""
    sex: Optional[str]
    count: int

class Part1Summary(BaseModel):
    """Summary statistics for Part 1"""
    total_penguins: int
    missing_values: Dict[str, int]
    numeric_stats: List[DescriptiveStats]
    species_counts: List[SpeciesCount]
    island_counts: List[IslandCount]
    sex_counts: List[SexCount]

# Part 2 Models
class HistogramBin(BaseModel):
    """Histogram bin data"""
    bin: str
    count: int

class CorrelationMatrix(BaseModel):
    """Correlation matrix data"""
    variables: List[str]
    correlations: List[List[float]]

class Part2Data(BaseModel):
    """Visualization data for Part 2"""
    variable: str
    histogram: List[HistogramBin]
    quartiles: Dict[str, float]

# Part 3 Models
class RegressionResult(BaseModel):
    """Simple regression result"""
    predictor: str
    target: str = "body_mass_g"
    intercept: float
    coefficient: float
    r_squared: float
    p_value: float
    equation: str
    residual_std: float

class MultipleRegressionResult(BaseModel):
    """Multiple regression result"""
    predictors: List[str]
    target: str = "body_mass_g"
    intercept: float
    coefficients: Dict[str, float]
    r_squared: float
    p_value: float
    residual_std: float

# Part 4 Models
class PredictionInput(BaseModel):
    """Input for prediction"""
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

class PredictionResult(BaseModel):
    """Prediction result"""
    predicted_species: str
    probabilities: Dict[str, float]
    confidence: float

class ConfusionMatrixData(BaseModel):
    """Confusion matrix data"""
    species: List[str]
    matrix: List[List[int]]

class ClassificationMetrics(BaseModel):
    """Classification model metrics"""
    accuracy: float
    precision: Dict[str, float]
    recall: Dict[str, float]
    f1_score: Dict[str, float]
    confusion_matrix: ConfusionMatrixData

class FeatureImportance(BaseModel):
    """Feature importance data"""
    feature: str
    importance: float

class Part4ModelInfo(BaseModel):
    """Model information for Part 4"""
    model_type: str
    metrics: ClassificationMetrics
    feature_importances: List[FeatureImportance]
    trained_on_samples: int
