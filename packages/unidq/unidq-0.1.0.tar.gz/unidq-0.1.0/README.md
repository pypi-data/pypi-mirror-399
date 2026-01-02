# UNIDQ: Unified Data Quality

[![PyPI version](https://badge.fury.io/py/unidq.svg)](https://pypi.org/project/unidq/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**A unified transformer architecture for multi-task data quality assessment.**

UNIDQ addresses 6 data quality tasks with a single model:
- ✅ Error Detection (F1=0.894, +42% vs Raha)
- ✅ Data Repair
- ✅ Missing Value Imputation (R²=0.941, +295% vs MICE)
- ✅ Label Noise Detection (F1=0.856, +28% vs Cleanlab)
- ✅ Label Classification
- ✅ Data Valuation

## Installation
```bash
pip install unidq
```

## Quick Start
```python
from unidq import UNIDQ, MultiTaskDataset, UNIDQTrainer

# Load your data
dataset = MultiTaskDataset(
    dirty_features=X_dirty,
    clean_features=X_clean,
    error_mask=errors,
    labels=y
)

# Initialize model
model = UNIDQ(n_features=X_dirty.shape[1])

# Train
trainer = UNIDQTrainer(model)
trainer.fit(dataset)

# Predict
results = model.predict(X_new)
print(f"Detected errors: {results['errors']}")
print(f"Imputed values: {results['imputed']}")
```


## Citation

If you use UNIDQ in your research, please cite:
```bibtex
@inproceedings{unidq2026,
  title={UNIDQ: A Unified Transformer Architecture for Multi-Task Data Quality},
  author={Your Name},
  booktitle={Proceedings of the VLDB Endowment},
  year={2026}
}
```

## License

MIT License
