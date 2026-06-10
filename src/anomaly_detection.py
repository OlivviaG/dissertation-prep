import numpy as np
import pandas as pd

# Anomaly Detection Function


# Anomaly Detection using Z-score method
def compute_zscore(df):
    # computes z-score for heart_rate
    df['heart_rate_zscore'] = (df['heart_rate'] - df['heart_rate_mean']) / df['heart_rate_std']
    # must handle cases where std is zero to avoid division by zero
    df['heart_rate_zscore'] = df['heart_rate_zscore'].replace([np.inf, -np.inf], 0).fillna(0) 
    return df

def flag_anomalies_zscore(df, threshold=2):
    # flags anomalies where absolute z-score exceeds threshold
    df['is_anomaly_zscore'] = np.abs(df['heart_rate_zscore']) > threshold
    
    return df


# Anomaly detection using Isolation Forest
from sklearn.ensemble import IsolationForest

def run_isolation_forest(df, features, train_days=30, contamination=0.05):
    """
    Train Isolation Forest on the first train_days rows (normal period)
    and predict anomalies across the full dataset.
    
    features: list of column names to use e.g. ['heart_rate', 'stress_level']
    """
    train_df = df.iloc[:train_days][features].dropna()
    full_df = df[features].dropna()

    model = IsolationForest(contamination=contamination, n_estimators=100, random_state=42)
    model.fit(train_df)

    df['isolation_forest_anomaly'] = False
    df.loc[full_df.index, 'isolation_forest_score'] = model.decision_function(full_df)
    df.loc[full_df.index, 'isolation_forest_anomaly'] = model.predict(full_df) == -1

    return df, model





if __name__ == "__main__":
    from time_series import generate_fake_data, compute_rolling_stats

    # Generate User C with anomaly spike
    df = generate_fake_data(mean=72, std=7, anomaly_start=45, anomaly_mean=95)
    df = compute_rolling_stats(df)
    df = compute_zscore(df)
    df = flag_anomalies_zscore(df)

    print(df[df['is_anomaly_zscore'] == True][['timestamp', 'heart_rate', 'heart_rate_zscore']])
    print(f"\nTotal anomalies: {df['is_anomaly_zscore'].sum()}")


if __name__ == "__main__":
    from time_series import generate_fake_data, compute_rolling_stats

    df = generate_fake_data(mean=72, std=7, anomaly_start=45, anomaly_mean=95)
    df = compute_rolling_stats(df)
    df = compute_zscore(df)
    df = flag_anomalies_zscore(df)
    df, model = run_isolation_forest(df, features=['heart_rate'])

    print("Z-score anomalies:", df['is_anomaly_zscore'].sum())
    print("Isolation Forest anomalies:", df['isolation_forest_anomaly'].sum())
    print("\nIsolation Forest flagged rows:")
    print(df[df['isolation_forest_anomaly'] == True][['timestamp', 'heart_rate', 'isolation_forest_score']])