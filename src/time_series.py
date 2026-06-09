import numpy as np
import pandas as pd
# Time Series Analysis

def generate_fake_data(n_days=80):     # takes parameter n_days (default 80)

    # for n_days, with some random noise
    timestamps = pd.date_range(start=pd.Timestamp.today(), periods=n_days, freq='D')

    # uses numpy to generate realistic looking heart rate ~70bpm 
    heart_rates = np.random.normal(loc=70, scale=10, size=n_days)
    heart_rates = np.clip(heart_rates, 50, 100)  # Ensure realistic bounds
    
    # returns a pandas DF with 2 columns: timestamp and heart_rate
    df = pd.DataFrame({'timestamp': timestamps, 'heart_rate': heart_rates})

    return df



def compute_rolling_stats(df, window=7):
    # computes rolling mean and std for heart_rate
    df['heart_rate_mean'] = df['heart_rate'].rolling(window=window).mean()
    df['heart_rate_std'] = df['heart_rate'].rolling(window=window).std()
    return df

def flag_anomalies(df, threshold=2):
    # flags anomalies where heart_rate deviates from mean by more than threshold * std
    df['is_anomaly'] = np.abs(df['heart_rate'] - df['heart_rate_mean']) >  (threshold * df['heart_rate_std'])
    return df




if __name__ == "__main__":
    df = generate_fake_data()
    df = compute_rolling_stats(df)
    df = flag_anomalies(df)
    print(df[df['is_anomaly'] == True])

