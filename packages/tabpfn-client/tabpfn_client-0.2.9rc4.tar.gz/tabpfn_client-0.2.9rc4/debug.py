from __future__ import annotations

import pandas as pd

from pathlib import Path
from tabpfn_client import TabPFNClassifier, TabPFNRegressor, get_access_token, set_access_token

# Path of the root directory
ROOT_DIR = Path("~/Downloads/")


def main():
    """Run the main function."""

    # Read the training set labels
    x_train = pd.read_csv(ROOT_DIR / "x_train_1.csv")     

    # Get the training set predictions
    y_train = pd.read_csv(ROOT_DIR / "y_train_1.csv")

    # Get the test set labels
    x_test = pd.read_csv(ROOT_DIR / "x_test_1.csv")

    # Get the API access token
    access_token = get_access_token()
    set_access_token(access_token)

    # Run multiple iterations of the model
    for _ in range(10):
        # Fit the model
        regressor = TabPFNRegressor(
            average_before_softmax=False,
            ignore_pretraining_limits=False,
            inference_precision="auto",
            n_estimators=8,
            random_state=42,
            softmax_temperature=0.9,
            paper_version=True,
        )
        regressor.fit(x_train, y_train)

        # Predict the test set labels
        y_pred = regressor.predict(x_test)

        # Print the predictions
        print(y_pred)

    pass
    


if __name__ == "__main__":
    main()