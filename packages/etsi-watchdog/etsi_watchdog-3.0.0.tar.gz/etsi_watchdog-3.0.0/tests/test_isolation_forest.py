# tests/test_isolation_forest.py

import pytest
import pandas as pd
from sklearn.datasets import make_blobs
from etsi.watchdog.models.isolation_forest import IsolationForestModel

def test_isolation_forest_basic():
    X, _ = make_blobs(n_samples=100, centers=1, cluster_std=0.6, random_state=0)
    data = pd.DataFrame(X, columns=["x", "y"])

    model = IsolationForestModel()
    model.fit(data)
    predictions = model.predict(data)

    assert len(predictions) == len(data)
    assert set(predictions).issubset({-1, 1})
