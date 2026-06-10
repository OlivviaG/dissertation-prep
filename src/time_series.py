import numpy as np
import pandas as pd
# Time Series Analysis


def generate_fake_data(mean, std, n_days=60, anomaly_start=None, anomaly_mean=None):

    timestamps = pd.date_range(start=pd.Timestamp.today(), periods=n_days, freq='D')

    if anomaly_start is not None and anomaly_mean is not None:
        normal_period = np.random.normal(loc=mean, scale=std, size=anomaly_start)
        anomaly_period = np.random.normal(loc=anomaly_mean, scale=std, size=n_days-anomaly_start)
        heart_rates = np.concatenate([normal_period, anomaly_period])
    else:
        heart_rates = np.random.normal(loc=mean, scale=std, size=n_days)

    heart_rates = np.clip(heart_rates, 40, 120)
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
    user_a = generate_fake_data(mean=65, std=3)
    user_b = generate_fake_data(mean=80, std=12)
    user_c = generate_fake_data(mean=72, std=7, anomaly_start=45, anomaly_mean=95)

    print("User A:", user_a.shape)
    print("User B:", user_b.shape)
    print("User C:", user_c.shape)
    print("\nUser C tail:")
    print(user_c.tail(20))