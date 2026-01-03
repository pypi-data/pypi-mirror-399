# ML Audit

> **Solves Data Lineage Blindness by tracking granular preprocessing steps.**

`ml-audit` is a lightweight Python library designed to bring transparency and reproducibility to data preprocessing. Unlike standard experiment trackers that treat preprocessing as a black box, this library records every granular transformation applied to your pandas DataFrame.

## Why ML Audit?

**It solves "Data Lineage Blindness".**

Most data science teams suffer from a gap in their experiment tracking:
*   **MLflow/W&B** track *metrics* (accuracy, loss) and *hyperparameters*. They often treat the cleaned dataset as a static artifact.
*   **DVC** tracks *file versions*. It tells you **that** the data changed from Version A to Version B.
*   **ML Audit** tells you **why** and **how** it changed. It logs: *"Imputed column 'Age' with mean (42.5), then Scaled with StandardScaler, then OneHotEncoded 'Gender'."*

## Features

- **Full Audit Trail**: Automatically logs every step (Imputation, Scaling, Encoding, etc.) into a JSON audit file.
- **Reproducibility**: Verify if your data pipeline produces the exact same result every time using hash validation.
- **Visualization**: Auto-generates an interactive HTML timeline of your preprocessing steps.
- **Comprehensive Operations**:
    - **Imputation**: mean, median, mode, constant, ffill, bfill.
    - **Scaling**: minmax, standard, robust, maxabs.
    - **Encoding**: onehot, label, target encoding.
    - **Balancing**: smote (via imblearn), oversample, undersample.
    - **Transformation**: log, sqrt, boxcox.
    - **Date Extraction**: Extract year, month, day from timestamps.
- **Multi-Column Support**: Apply operations to lists of columns efficiently.
- **Generic Support**: Track *any* arbitrary pandas method (e.g., dropna, rename).

## Installation

You can install `ml-audit` via pip:

```bash
pip install ml-audit
```

For SMOTE balancing support, install with the `balance` extra:

```bash
pip install ml-audit[balance]
```

## Quick Start

### 1. Initialize the Recorder

```python
import pandas as pd
from ml_audit import AuditTrialRecorder

# Load your data
df = pd.read_csv("data.csv")

# Initialize the auditor wrapped around your dataframe
auditor = AuditTrialRecorder(df, name="experiment_v1")
```

### 2. Apply Preprocessing

Chain methods fluently. Operations are applied immediately to `auditor.current_df`.

```python
auditor.filter_rows("age", ">=", 18) \
       .impute(["salary", "score"], strategy='median') \
       .scale(["salary", "age"], method='minmax') \
       .encode("gender", method='onehot') \
       .balance_classes("churn", strategy='oversample') # Handles imbalanced data
```

### 3. Access Data

```python
processed_df = auditor.current_df
print(processed_df.head())
```

### 4. Export & Visualize

Save the audit trail. This will generate a JSON file (`audit_trails/`) and an HTML visualization (`visualizations/`).

```python
auditor.export_audit_trail("audit.json")
# Output:
# - audit_trails/audit.json
# - visualizations/audit.html
```

## Detailed Documentation

### Multi-Column Operations
All major preprocessing methods accept either a single string or a list of strings for column names.

```python
# Scale multiple columns at once
auditor.scale(["height", "weight", "bmi"], method='standard')
```

### Generic Pandas Tracking
For operations not natively built-in, use `track_pandas` to record any DataFrame method.

```python
# Track a rename operation
auditor.track_pandas("rename", columns={"old_name": "new_name"})

# Track dropping NaNs
auditor.track_pandas("dropna", subset=["critical_col"])
```

### Reproducibility Check
Verify that replaying your logs produces the exact same data hash as the current state.

```python
if auditor.verify_reproducibility():
    print("Pipeline is scientifically reproducible!")
else:
    print("Pipeline result mismatch!")
```

## Visualization
Open the generated HTML file in `visualizations/` to see a timeline like this:

- **Step 1: Load Data** (Shape: 1000x5)
- **Step 2: Impute** (`salary` -> median)
- **Step 3: Scale** (`age` -> minmax)

## License
MIT License. Free to use for personal and commercial projects.
