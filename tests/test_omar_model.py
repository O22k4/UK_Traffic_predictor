import pandas as pd
from Omar_model import train_and_save_model


def test_train_and_save_model(tmp_path, monkeypatch):
    # Fake dataset
    df = pd.DataFrame({
        "DateTime": pd.date_range("2024-01-01", periods=30, freq="H"),
        "Vehicles": range(30)
    })

    # Mock pandas.read_csv
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: df)

    model_path = tmp_path / "model.pkl"

    model = train_and_save_model("fake.csv", model_path)

    assert model is not None
    assert model_path.exists()
