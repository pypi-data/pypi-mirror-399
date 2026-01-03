import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    """Helper to load and format data correctly."""
    df = pd.read_csv(filepath)

    # Ensure column names are lowercase
    df.columns = [c.lower() for c in df.columns]

    # Rename common variations
    rename_map = {"open_time": "timestamp", "date": "timestamp", "vol": "volume"}
    df = df.rename(columns=rename_map)

    # Ensure timestamp is integer (unix seconds) if it's a string
    if df["timestamp"].dtype == "object":
        try:
            # Convert to nanoseconds then to seconds
            df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(np.int64) // 10**9
        except Exception:
            pass

    return df
