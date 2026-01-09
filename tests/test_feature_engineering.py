import pandas as pd
from Omar_model import train_and_save_model
import joblib

def test_feature_engineering(tmp_path, monkeypatch):
    # --- Mock dataset ---
    df = pd.DataFrame({
        "DateTime": pd.date_range("2024-01-01", periods=18, freq="H"),
        "Vehicles": [10, 12, 14, 20, 22, 24, 30, 32, 34, 40, 42, 44, 50, 52, 54, 60, 62, 64]
    })

    # Monkeypatch read_csv to return our fake df
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: df.copy())

    # Path for saved model
    model_path = tmp_path / "model.pkl"

    # Call the function
    model = train_and_save_model("fake.csv", model_path)

    # --- Feature engineering checks ---
    df_processed = pd.read_csv("fake.csv")  # We use the original for checks
    df_processed['DateTime'] = pd.to_datetime(df_processed['DateTime'], errors='coerce')
    df_processed['Hour'] = df_processed['DateTime'].dt.hour
    df_processed['DayOfWeek'] = df_processed['DateTime'].dt.dayofweek
    df_processed['Month'] = df_processed['DateTime'].dt.month
    df_processed['Weekend'] = df_processed['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
    df_processed['RushHour'] = df_processed['Hour'].apply(lambda h: 1 if (7 <= h <= 9) or (16 <= h <= 19) else 0)

    # Test new columns exist
    for col in ['Hour', 'DayOfWeek', 'Month', 'Weekend', 'RushHour']:
        assert col in df_processed.columns

    # Test RushHour values are 0 or 1
    assert set(df_processed['RushHour'].unique()).issubset({0, 1})

    # Test model was saved
    assert model_path.exists()
