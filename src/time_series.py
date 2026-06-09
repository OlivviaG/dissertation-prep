import numpy as np
import pandas as pd
# Time Series Analysis

def generate_fake_data(n_days=60):     # takes parameter n_days (default 60)

    # for n_days, with some random noise
    timestamps = pd.date_range(start=pd.Timestamp.today(), periods=n_days, freq='D')

    # uses numpy to generate realistic looking heart rate ~70bpm 
    heart_rates = np.random.normal(loc=70, scale=10, size=n_days)
    heart_rates = np.clip(heart_rates, 50, 100)  # Ensure realistic bounds
    
    # returns a pandas DF with 2 columns: timestamp and heart_rate
    df = pd.DataFrame({'timestamp': timestamps, 'heart_rate': heart_rates})

    return df



if __name__ == "__main__":
    df = generate_fake_data()
    print(df.shape)
    print(df.head())