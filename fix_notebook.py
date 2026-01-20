import json

# Read the notebook
with open('MBU_Gap_Analyzer.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find and fix the Prophet cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'Regenerating forecast with stable data' in source and 'prophet_df = daily_updates' not in source:
            # Build the new source
            new_source = '''# FIX: Prophet forecast was producing wild oscillations from -150M to +150M
# This is because Prophet overfits to the sparse post-September data
# Solution: Use only stable pre-September data and clip forecasts to reasonable bounds

print("[INFO] Regenerating forecast with stable data only...\\n")

# First, create prophet_df from daily_updates (Prophet requires 'ds' and 'y' columns)
prophet_df = daily_updates[['date', 'total_updates']].copy()
prophet_df.columns = ['ds', 'y']

# Filter to stable period (before the sharp drop in September 2025)
cutoff_date = pd.Timestamp('2025-09-01')
stable_data = prophet_df[prophet_df['ds'] < cutoff_date].copy()

print(f"[INFO] Using stable period: {stable_data['ds'].min().date()} to {stable_data['ds'].max().date()}")
print(f"[INFO] Stable period has {len(stable_data)} data points")

# Calculate baseline statistics from stable period
baseline_avg = stable_data['y'].mean()
baseline_std = stable_data['y'].std()
print(f"[INFO] Baseline avg updates: {baseline_avg:,.0f}/day")

# Retrain Prophet on stable data with heavy regularization
model_fixed = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.001,  # Very low to prevent overfitting
    seasonality_prior_scale=0.1,
    interval_width=0.80
)

# Suppress Stan output
import logging
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

model_fixed.fit(stable_data)

# Forecast to school admission season 2026
days_to_add = (pd.Timestamp('2026-08-01') - stable_data['ds'].max()).days
future_fixed = model_fixed.make_future_dataframe(periods=days_to_add)
forecast_fixed = model_fixed.predict(future_fixed)

# CRITICAL: Clip to reasonable bounds (no negative values!)
forecast_fixed['yhat'] = forecast_fixed['yhat'].clip(lower=0, upper=baseline_avg * 3)
forecast_fixed['yhat_lower'] = forecast_fixed['yhat_lower'].clip(lower=0)
forecast_fixed['yhat_upper'] = forecast_fixed['yhat_upper'].clip(lower=0, upper=baseline_avg * 4)

# Replace original forecast with fixed version
forecast = forecast_fixed.copy()

print("[OK] Fixed forecast complete!")
print(f"[INFO] Forecast range: {forecast['ds'].min().date()} to {forecast['ds'].max().date()}")

# Show school admission season prediction
school_season = forecast[(forecast['ds'] >= '2026-06-01') & (forecast['ds'] <= '2026-07-31')]
print(f"[INFO] School Admission Season prediction: {school_season['yhat'].mean():,.0f} updates/day")'''
            
            # Replace the cell source
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]] + [new_source.split('\n')[-1]]
            print(f'Fixed cell {i}')
            break

# Write back
with open('MBU_Gap_Analyzer.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print('Notebook updated!')
