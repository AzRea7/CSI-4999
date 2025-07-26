import os
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from joblib import dump

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
    # Aggregate average price per year
    yearly = df.groupby("year")["price"].mean()
    
    print("Yearly averages:")
    print(yearly)

    # Train ARIMA model (simple ARIMA(1,1,1))
    model = ARIMA(yearly, order=(1, 1, 1))
    fitted_model = model.fit()

    # Forecast next 20 years
    FUTURE_YEARS = 20  # Forecast 20 years beyond last year in dataset
    future = fitted_model.forecast(steps=FUTURE_YEARS)
    future_years = list(range(yearly.index.max() + 1, yearly.index.max() + 1 + FUTURE_YEARS))

    forecast = {str(year): round(price, 2) for year, price in zip(future_years, future)}
    print("📈 Forecast:", forecast)

    return forecast

def main():
    path = download_dataset()
    df = load_data(path)
    forecast_dict = train_arima(df)
    dump(forecast_dict, MODEL_FILENAME)
    print(f"Forecast saved to {MODEL_FILENAME}")

if __name__ == "__main__":
    main()
