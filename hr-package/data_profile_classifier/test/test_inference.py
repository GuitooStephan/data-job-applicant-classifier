import os
import unittest
import pandas as pd
from pathlib import Path
from data_profile_classifier import train, inference


class TestInference(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = Path(__file__).parent.joinpath('data')

    def test_inference_success(self):
        """Test inference success"""
        train_data_raw = pd.read_csv(
            self.data_dir.joinpath('dataset_train_test.csv'), sep=';')
        y_val, y_pred = train.build_model(train_data_raw, self.data_dir)

        test_data_raw = pd.read_csv(
            self.data_dir.joinpath('dataset_predict.csv'), sep=';')
        y_pred_test = inference.predict(test_data_raw, self.data_dir)
        assert len(test_data_raw) == len(y_pred_test)

    def test_inference_failure(self):
        """Test inference failure"""
        test_data_raw = pd.read_csv(
            self.data_dir.joinpath('dataset_predict.csv'), sep=';')
        self.assertRaises(FileNotFoundError, inference.predict,
                          data=test_data_raw, models_dir=self.data_dir)

    def tearDown(self) -> None:
        for p in self.data_dir.glob("*.joblib"):
            p.unlink()
