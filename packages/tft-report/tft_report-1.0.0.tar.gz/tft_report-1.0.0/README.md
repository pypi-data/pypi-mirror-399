# TFT Report Generator

Automated Temporal Fusion Transformer modeling with publication-ready report generation.

## Features

- **Automatic Data Analysis**: EDA with GPT-powered insights
- **TFT Architecture Visualization**: Model structure diagram with hyperparameters
- **Model Training**: Automated training with progress tracking
- **Bootstrap Significance Testing**: Parameter stability analysis
- **Variable Importance Analysis**: SHAP-like interpretability
- **Prediction Visualization**: Actual vs Predicted with uncertainty bands
- **Word Document Report**: Complete academic-style report

## Installation

```bash
pip install git+https://github.com/sdkparkforbi/tft-report.git
```

## Requirements

### Minimum System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | >= 3.9 |
| RAM | >= 8 GB (16 GB recommended) |
| GPU | Optional (CPU works, GPU faster) |
| Storage | >= 2 GB free space |

### Dependencies

```
pytorch>=2.0.0
pytorch-forecasting>=1.0.0
lightning>=2.0.0
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
python-docx>=0.8.0
openai>=1.0.0
```

### API Keys

- **OpenAI API Key**: Required for GPT-powered explanations
  - Set as environment variable: `OPENAI_API_KEY`
  - Or pass directly: `api_key='your-key'`
  - Colab: Store in Secrets as `OPENAI_API_KEY`

## Quick Start

### Google Colab (Recommended)

```python
# Install
!pip install git+https://github.com/sdkparkforbi/tft-report.git -q

# Import
from tft_report import generate_tft_report
import pandas as pd
import numpy as np

# Sample data
np.random.seed(42)
n_patients, n_days = 5, 60

df = pd.DataFrame({
    'time_idx': np.tile(range(n_days), n_patients),
    'patient': np.repeat([f'P{i}' for i in range(n_patients)], n_days),
    'glucose': np.random.normal(140, 20, n_patients * n_days),
    'insulin': np.random.randint(8, 16, n_patients * n_days),
    'dayofweek': np.tile(np.arange(n_days) % 7, n_patients),
})

# Generate report
generate_tft_report(
    df,
    target='glucose',
    group_id='patient',
    time_idx='time_idx',
    known_reals=['insulin', 'dayofweek'],
    download=True
)
```

### Local Python

```python
from tft_report import generate_tft_report
import pandas as pd

df = pd.read_csv('your_data.csv')

generate_tft_report(
    df,
    target='glucose',
    group_id='patient',
    time_idx='time_idx',
    api_key='your-openai-api-key'
)
```

## Configuration

```python
generate_tft_report(
    df,
    target='glucose',
    group_id='patient',
    time_idx='time_idx',
    known_reals=['insulin', 'dayofweek'],  # Known future variables
    unknown_reals=['glucose'],              # Unknown future variables
    static_categoricals=['patient'],        # Static categorical variables
    config={
        'max_encoder_length': 14,           # Lookback window
        'max_prediction_length': 3,         # Forecast horizon
        'hidden_size': 32,                  # Model hidden size
        'attention_head_size': 2,           # Number of attention heads
        'lstm_layers': 2,                   # Number of LSTM layers
        'dropout': 0.1,                     # Dropout rate
        'batch_size': 32,                   # Training batch size
        'max_epochs': 50,                   # Maximum training epochs
        'n_bootstrap': 100,                 # Bootstrap iterations
    },
    verbose=True,
    download=True
)
```

## Data Format

Your DataFrame must have:

| Column | Description | Example |
|--------|-------------|---------|
| `time_idx` | Integer time index | 0, 1, 2, ... |
| `group_id` | Group identifier | 'P0', 'P1', ... |
| `target` | Target variable to predict | glucose values |
| Other columns | Covariates | insulin, dayofweek |

### Example Data Structure

```
   time_idx patient  glucose  insulin  dayofweek
0         0      P0   145.23       10          0
1         1      P0   138.45       12          1
2         2      P0   142.67       11          2
...
```

## Output

The generated zip file contains:

1. **Word Document** (`tft_analysis_report.docx`)
   - Introduction
   - Data Description with tables and figures
   - Model Specification (architecture, hyperparameters)
   - Results (performance metrics, variable importance)
   - Bootstrap significance analysis
   - Conclusion

2. **Figures** (PNG, 300 DPI)
   - Target distribution histogram
   - Time series plots
   - TFT architecture diagram
   - Prediction vs Actual scatter
   - Uncertainty visualization
   - Variable importance bar chart
   - Attention weights (if available)

## Report Structure

```
1. Introduction
   - Dataset overview
   - TFT methodology rationale

2. Data Description
   - Table 1: Dataset characteristics
   - Figure 1: Target distribution
   - Figure 2: Time series by group

3. Model Specification
   - 3.1 TFT Architecture (with diagram)
   - 3.2 Hyperparameters (Table 2)

4. Results
   - 4.1 Model Performance (MAE, RMSE)
   - 4.2 Variable Importance
   - 4.3 Bootstrap Significance

5. Conclusion
```

## GPU Acceleration

For faster training, use GPU:

### Google Colab
- Runtime → Change runtime type → GPU

### Local
```python
import torch
print(f"GPU available: {torch.cuda.is_available()}")
```

## Troubleshooting

### "OpenAI API key not found"
```python
# Option 1: Pass directly
generate_tft_report(df, ..., api_key='sk-...')

# Option 2: Environment variable
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'

# Option 3: Colab Secrets
# Add OPENAI_API_KEY in Colab's Secrets (key icon)
```

### "CUDA out of memory"
```python
# Reduce batch size and model size
generate_tft_report(df, ..., config={
    'batch_size': 16,
    'hidden_size': 16,
    'attention_head_size': 1
})
```

### "Module not found"
```bash
pip install pytorch-forecasting lightning python-docx openai
```

## License

MIT License

## Citation

If you use this package in your research, please cite:

```
@software{tft_report,
  title = {TFT Report Generator},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/sdkparkforbi/tft-report}
}
```
