"""Tutorial: DFM for Macro Data

This tutorial demonstrates the complete workflow for training and prediction
using macro data with multiple target variables.

Targets: KOEQUIPTE (Investment), KOWRCCNSE (Consumption), KOIMPCONA (Imports)
"""

import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import pandas as pd
import numpy as np
from datetime import datetime
from dfm_python import DFM, DFMDataModule
from dfm_python.config import DFMConfig
from dfm_python.utils.misc import TimeIndex

# sktime imports for preprocessing
from sktime.transformations.compose import TransformerPipeline
from sktime.transformations.series.impute import Imputer
from sklearn.preprocessing import StandardScaler

print("=" * 80)
print("DFM Tutorial: Macro Data")
print("=" * 80)

# ============================================================================
# Step 1: Load Data
# ============================================================================
print("\n[Step 1] Loading macro data...")
data_path = project_root / "data" / "macro.csv"
df = pd.read_csv(data_path)

print(f"   Data shape: {df.shape}")
print(f"   Columns: {len(df.columns)}")

# ============================================================================
# Step 2: Prepare Data
# ============================================================================
print("\n[Step 2] Preparing data...")

# Target variables (multiple targets)
target_cols = ["KOEQUIPTE", "KOWRCCNSE", "KOIMPCONA"]  # Investment, Consumption, Imports

# Select a subset of series for faster execution
# Use fewer series for faster execution
selected_cols = [
    # Employment (reduced)
    "KOEMPTOTO", "KOHWRWEMP",
    # Consumption (reduced)
    "KOWRCCNSE", "KOWRCDURE",
    # Investment (reduced)
    "KOIMPCONA",
    # Production (reduced)
    "KOCONPRCF",
    # Targets (included in selected_cols)
] + target_cols

# Filter to only columns that exist in the data
selected_cols = [col for col in selected_cols if col in df.columns]

# Filter data (include date column for time index)
df_processed = df[selected_cols + ["date"]].copy()
print(f"   Selected {len(selected_cols)} series (including target)")
print(f"   Series: {selected_cols[:5]}...")

# Parse date column
df_processed["date"] = pd.to_datetime(df_processed["date"])
df_processed = df_processed.sort_values("date")

# Remove rows with all NaN
df_processed = df_processed.dropna(how='all')

# Use only recent data for faster execution
# Take last 100 periods (further reduced for faster execution)
max_periods = 100
if len(df_processed) > max_periods:
    df_processed = df_processed.iloc[-max_periods:]
    print(f"   Using last {max_periods} periods for faster execution")

print(f"   Data shape after cleaning: {df_processed.shape}")

# Check for missing values
missing_before = df_processed.isnull().sum().sum()
print(f"   Missing values before preprocessing: {missing_before} ({missing_before/df_processed.size*100:.1f}%)")

# ============================================================================
# Step 2.5: Create Preprocessing Pipeline with sktime
# ============================================================================
print("\n[Step 2.5] Creating preprocessing pipeline with sktime...")

# Simplified preprocessing: Apply difference to target series manually, then use unified pipeline
# This is faster than ColumnEnsembleTransformer for small datasets

# Apply difference transformation to target series manually (for chg transformation)
for target_col in target_cols:
    if target_col in df_processed.columns:
        target_series = df_processed[target_col].values
        # Apply first difference
        target_diff = np.diff(target_series, prepend=target_series[0])
        df_processed[target_col] = target_diff
        print(f"   Applied difference transformation to {target_col}")

# Note: date column will be removed by DataModule when time_index_column='date' is used
# For preprocessing, we need to temporarily remove it to avoid issues with datetime columns
# Store date column separately for reference (though DataModule will extract it)
if 'date' in df_processed.columns:
    # Temporarily remove date column for preprocessing (DataModule will handle it)
    df_for_preprocessing = df_processed.drop(columns=['date'])
else:
    df_for_preprocessing = df_processed

# Create simplified preprocessing pipeline: Imputation → Scaling
# (Transformations already applied manually above)
# This pipeline will be fitted and used to preprocess data
# Then passed to DataModule for statistics extraction (Mx/Wx)
preprocessing_pipeline = TransformerPipeline(
    steps=[
        ('impute_ffill', Imputer(method="ffill")),  # Forward fill missing values
        ('impute_bfill', Imputer(method="bfill")),  # Backward fill remaining NaNs
        ('scaler', StandardScaler())  # Unified scaling for all series
    ]
)

def _get_fitted_scaler(pipeline, data_frame):
    """Extract fitted scaler; if not fitted, fit it on provided data."""
    # Drop non-numeric columns before fitting
    numeric_cols = data_frame.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < len(data_frame.columns):
        data_frame = data_frame[numeric_cols].copy()
    
    steps_attr = getattr(pipeline, "steps_", None)
    candidate = (steps_attr or pipeline.steps)[-1][1]
    if not hasattr(candidate, "n_features_in_"):
        candidate = candidate.fit(data_frame)
    return candidate

print("   Pipeline: Imputer(ffill) → Imputer(bfill) → StandardScaler")
print(f"   Transformations: {', '.join(target_cols)} use difference (chg), others use linear")
print("   Applying preprocessing pipeline...")

# Fit preprocessing pipeline on training data once (without date column)
fitted_pipeline = preprocessing_pipeline.clone().fit(df_for_preprocessing)
df_preprocessed = fitted_pipeline.transform(df_for_preprocessing)

# Ensure output is DataFrame
if isinstance(df_preprocessed, np.ndarray):
    df_preprocessed = pd.DataFrame(df_preprocessed, columns=df_for_preprocessing.columns, index=df_for_preprocessing.index)
elif not isinstance(df_preprocessed, pd.DataFrame):
    df_preprocessed = pd.DataFrame(df_preprocessed)

# Add date column back for DataModule to extract (if it exists)
if 'date' in df_processed.columns:
    df_preprocessed['date'] = df_processed['date'].values

# Ensure output is DataFrame
if isinstance(df_preprocessed, np.ndarray):
    df_preprocessed = pd.DataFrame(df_preprocessed, columns=df_processed.columns, index=df_processed.index)
elif not isinstance(df_preprocessed, pd.DataFrame):
    df_preprocessed = pd.DataFrame(df_preprocessed)

missing_after = df_preprocessed.isnull().sum().sum()
print(f"   Missing values after preprocessing: {missing_after}")
print(f"   Preprocessed data shape: {df_preprocessed.shape}")

# Verify standardization (exclude date column if present)
df_for_check = df_preprocessed.drop(columns=['date']) if 'date' in df_preprocessed.columns else df_preprocessed
mean_vals = df_for_check.mean()
std_vals = df_for_check.std()
max_mean = float(mean_vals.abs().max())
max_std_dev = float((std_vals - 1.0).abs().max())
print(f"   Standardization check - Max |mean|: {max_mean:.6f} (should be ~0)")
print(f"   Standardization check - Max |std - 1|: {max_std_dev:.6f} (should be ~0)")

# Update df_processed to use preprocessed data
df_processed = df_preprocessed

# ============================================================================
# Step 3: Create Configuration
# ============================================================================
print("\n[Step 3] Creating configuration...")

# Create frequency dict (maps column names to frequencies)
# All series are monthly, so use 'm' for all
frequency_dict = {col: "m" for col in selected_cols}

# Create blocks config - new format: {"block_name": {"num_factors": int, "series": [str]}}
# VAR(1) is specified globally via ar_lag parameter
blocks_config = {
    "Block_Global": {
        "num_factors": 1,  # Reduced to 1 for faster execution
        "series": selected_cols  # All series in one block
    }
}

# Create DFM config
config = DFMConfig(
    frequency=frequency_dict,
    blocks=blocks_config,
    clock="m",  # Monthly clock frequency
    ar_lag=1,   # VAR(1) - first-order autoregressive (global parameter)
    max_iter=3,  # Further reduced for faster execution
    threshold=1e-2  # More relaxed threshold for faster convergence
)

print(f"   Number of series: {len(selected_cols)}")
print(f"   Number of factors: {config.blocks['Block_Global']['num_factors']}")
print(f"   Factor dynamics: VAR(1) (ar_lag=1)")
print(f"   Target series: {', '.join(target_cols)} ({len(target_cols)} targets)")

# ============================================================================
# Step 4: Create DataModule
# ============================================================================
print("\n[Step 4] Creating DataModule...")

# Create DataModule with preprocessed data
# Since data is already preprocessed, use preprocessed=True
# Pipeline is already fitted, so it will only be used for statistics extraction
# time_index_column='date' will extract time index from DataFrame and remove the column
data_module = DFMDataModule(
    config=config,
    data=df_processed,  # Pass DataFrame directly (not .values)
    time_index_column='date',  # Extract time index from 'date' column and exclude it from data
    pipeline=fitted_pipeline,  # Already fitted pipeline
    preprocessed=True,  # Data is already preprocessed
    target_series=target_cols  # Specify multiple target series
)
data_module.setup()

print(f"   DataModule created successfully")
if hasattr(data_module, 'data_processed') and data_module.data_processed is not None:
    print(f"   Processed data shape: {data_module.data_processed.shape}")
else:
    print(f"   Data shape: {df_processed.shape}")
if data_module.time_index is not None:
    print(f"   Time range: {data_module.time_index[0]} to {data_module.time_index[-1]}")

# ============================================================================
# Step 5: Train Model
# ============================================================================
print("\n[Step 5] Training DFM model...")

# Create DFM model
# Note: mixed_freq is now auto-detected from DataModule
# Mixed frequency will be automatically detected based on config frequencies
model = DFM()
model.load_config(config)  # Load config

# Get initialization parameters from datamodule
init_params = data_module.get_initialization_params()
X = init_params['X']
Mx = init_params['Mx']
Wx = init_params['Wx']

# Fit model directly (DFM uses fit() method, not Lightning trainer)
training_state = model.fit(X=X, Mx=Mx, Wx=Wx, datamodule=data_module)

print("   Training completed!")
print(f"   Converged: {training_state.converged}")
print(f"   Iterations: {training_state.num_iter}")
print(f"   Log-likelihood: {training_state.loglik:.4f}")

# ============================================================================
# Step 6: Prediction
# ============================================================================
print("\n[Step 6] Making predictions...")

X_forecast = None
Z_forecast = None
X_forecast_history = None
Z_forecast_history = None
# Use df_for_preprocessing (without date column) for scaler extraction
scaler = _get_fitted_scaler(fitted_pipeline, df_for_preprocessing)

try:
    # Predict with default horizon (uses target_series from DataModule)
    X_forecast, Z_forecast = model.predict(horizon=6)
    
    print(f"   Forecast shape: {X_forecast.shape}")
    print(f"   Factor forecast shape: {Z_forecast.shape}")
    
    # X_forecast contains forecasts for all target series
    print(f"   Forecast shape: {X_forecast.shape} (horizon x {len(target_cols)} targets)")
    print(f"   First period forecasts:")
    for i, target_col in enumerate(target_cols):
        print(f"     {target_col}: {X_forecast[0, i]:.6f}")
    
    # Verify inverse-transform consistency (round-trip through scaler)
    try:
        restored = scaler.inverse_transform(scaler.transform(X_forecast))
        assert np.allclose(restored, X_forecast, atol=1e-6)
        print("   ✔ Inverse-transform check passed (predict)")
    except Exception as inv_err:
        print(f"   ⚠ Inverse-transform check failed (predict): {inv_err}")
    
    # Note: history parameter was removed - prediction uses full history by default
    
except ValueError as e:
    print(f"   Prediction failed: {e}")
    print("   Note: This may indicate numerical instability. Try:")
    print("   - Using more training iterations")
    print("   - Adjusting data transformations")
    print("   - Using different factor configurations")

# ============================================================================
# Step 7: Summary
# ============================================================================
print("\n" + "=" * 80)
print("Tutorial Summary")
print("=" * 80)
print(f"✅ Data loaded: {df.shape[0]} rows, {len(selected_cols)} series")
print(f"✅ Model trained: {len(selected_cols)} series, {config.blocks['Block_Global']['num_factors']} factors, VAR(1) dynamics")
if X_forecast is not None:
    print(f"✅ Predictions generated: {X_forecast.shape[0]} periods ahead")
else:
    print(f"⚠️  Predictions: Failed (see error message above)")
print(f"✅ Target series: {', '.join(target_cols)} ({len(target_cols)} targets)")
print("=" * 80)
