"""
UNIDQ: Unified Transformer for Multi-Task Data Quality
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .model import UNIDQ, UNIDQConfig
from .dataset import MultiTaskDataset
from .trainer import UNIDQTrainer
from .evaluation import evaluate_all_tasks

__all__ = [
    "UNIDQ",
    "UNIDQConfig", 
    "MultiTaskDataset",
    "UNIDQTrainer",
    "evaluate_all_tasks",
]
