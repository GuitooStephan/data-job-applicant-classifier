import os
import unittest
import pandas as pd
from pathlib import Path
from data_profile_classifier import train


class TestTraining(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = Path(__file__).parent.joinpath('data')

    def test_training_success(self):
        """Test training success"""
        train_data_raw = pd.read_csv(
            self.data_dir.joinpath('dataset_train_test.csv'), sep=';')
        y_val, y_pred = train.build_model(train_data_raw, self.data_dir)
        assert os.path.isfile(self.data_dir.joinpath('pipeline.joblib'))
        assert os.path.isfile(self.data_dir.joinpath('label_encoder.joblib'))
        assert len(y_val) == len(y_pred)

    def tearDown(self) -> None:
        for p in self.data_dir.glob("*.joblib"):
            p.unlink()
