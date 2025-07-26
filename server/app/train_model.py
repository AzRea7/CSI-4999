import os
import numpy as np
import pandas as pd
import kagglehub
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

def load_dataset():
    print(" Downloading dataset from KaggleHub...")
    dataset_path = kagglehub.dataset_download("yasserh/housing-prices-dataset")
    csv_path = os.path.join(dataset_path, "Housing.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Housing.csv not found at {csv_path}")

    print(f" Loading dataset from: {csv_path}")
    return pd.read_csv(csv_path)

def train_model(df):
    print(" Selecting features and target")
    X = df[["area", "bedrooms", "bathrooms"]]
    y = df["price"]

    # Optionally add data validation or fillna if needed later
    # X.fillna(0, inplace=True)

    print(" Training Linear Regression model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f" Model trained. R²: {r2:.2f}, RMSE: {rmse:.2f}")
    return model

def save_model(model, filename="model.pkl"):
    model_path = os.path.join(os.path.dirname(__file__), filename)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f" Model saved to: {model_path}")

if __name__ == "__main__":
    try:
        df = load_dataset()
        model = train_model(df)
        save_model(model)
    except Exception as e:
        print(f" Error during model training: {e}")
