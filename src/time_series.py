import numpy as np
import pandas as pd
import plotly.graph_objects as go

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


def plot_user_baseline(df, user_name="User"):
    """Plot heart rate with rolling mean, normal range band, and anomaly points."""
    
    fig = go.Figure()

    # Normal range band (mean ± 2 std)
    fig.add_trace(go.Scatter(
        x=pd.concat([df['timestamp'], df['timestamp'].iloc[::-1]]),
        y=pd.concat([
            df['heart_rate_mean'] + 2 * df['heart_rate_std'],
            (df['heart_rate_mean'] - 2 * df['heart_rate_std']).iloc[::-1]
        ]),
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Normal Range'
    ))

    # Rolling mean line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['heart_rate_mean'],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Rolling Mean'
    ))

    # Actual heart rate line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['heart_rate'],
        mode='lines',
        line=dict(color='gray', width=1),
        name='Heart Rate'
    ))

    # Anomaly points in red
    anomalies = df[df['is_anomaly'] == True]
    fig.add_trace(go.Scatter(
        x=anomalies['timestamp'],
        y=anomalies['heart_rate'],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Anomaly'
    ))

    fig.update_layout(
        title=f"{user_name} — Personal Baseline",
        xaxis_title="Date",
        yaxis_title="Heart Rate (bpm)"
    )

    return fig

if __name__ == "__main__":
    user_a = generate_fake_data(mean=65, std=3)
    user_b = generate_fake_data(mean=80, std=12)
    user_c = generate_fake_data(mean=72, std=7, anomaly_start=45, anomaly_mean=95)

    for name, df in [("User A", user_a), ("User B", user_b), ("User C", user_c)]:
        df = compute_rolling_stats(df)
        df = flag_anomalies(df)
        anomaly_count = df['is_anomaly'].sum()
        print(f"{name}: {anomaly_count} anomalies flagged")

if __name__ == "__main__":
    user_c = generate_fake_data(mean=72, std=7, anomaly_start=45, anomaly_mean=95)
    user_c = compute_rolling_stats(user_c)
    user_c = flag_anomalies(user_c)
    
    fig = plot_user_baseline(user_c, user_name="User C")
    fig.show()