import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from joblib import dump
import numpy as np

# Constants
DATASET_ID = "prevek18/ames-housing-dataset"
MODEL_FILENAME = "house_price_model.joblib"

def download_dataset():
    import kagglehub
    dataset_path = kagglehub.dataset_download(DATASET_ID)
    return os.path.join(dataset_path, "AmesHousing.csv")

def load_data(filepath):
    df = pd.read_csv(filepath)
    df = df.loc[:, ~df.columns.str.contains('#NAME?', case=False, na=False)]
    df = df[["Yr Sold", "SalePrice"]].dropna()
    df.columns = ["year", "price"]
    return df

def train_arima(df):
    yearly = df.groupby("year")["price"].mean()

    smoothed = yearly.ewm(span=3).mean()
    log_prices = np.log(smoothed)

    print("Smoothed log-transformed average prices:")
    print(log_prices)

    # Fit ARIMA on smoothed log prices
    model = ARIMA(log_prices, order=(1, 1, 1))
    fitted_model = model.fit()

    # Forecast 20 years
    FUTURE_YEARS = 20
    forecast_log = fitted_model.get_forecast(steps=FUTURE_YEARS)
    forecast_values = forecast_log.predicted_mean
    conf_int = forecast_log.conf_int()

    future = np.exp(forecast_values)
    lower = np.exp(conf_int.iloc[:, 0])
    upper = np.exp(conf_int.iloc[:, 1])

    future_years = list(range(yearly.index.max() + 1, yearly.index.max() + 1 + FUTURE_YEARS))

    forecast_dict = {
        "forecast": {str(y): round(p, 2) for y, p in zip(future_years, future)},
        "lower": {str(y): round(p, 2) for y, p in zip(future_years, lower)},
        "upper": {str(y): round(p, 2) for y, p in zip(future_years, upper)},
        "confidence": 95
    }

    print("Forecast with Smoothing + Confidence Interval:")
    print(forecast_dict)

    return forecast_dict

def main():
    path = download_dataset()
    df = load_data(path)
    forecast_dict = train_arima(df)
    dump(forecast_dict, MODEL_FILENAME)
    print(f"Forecast saved to {MODEL_FILENAME}")

if __name__ == "__main__":
    main()
