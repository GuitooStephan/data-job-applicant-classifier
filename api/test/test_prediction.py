import unittest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from main import app


class TestPredictions(unittest.TestCase):
    def setUp(self) -> None:
        self.predictions = pd.DataFrame(
            [{
                'entreprise': 'Google',
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': 'Paris'
            }, {
                'entreprise': 'Microsoft',
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': 'Paris'
            }],
            columns=['entreprise', 'technologies',
                     'diplome', 'experience', 'ville']
        )
        self.predictions_with_missing_fields = pd.DataFrame(
            [{
                'entreprise': 'Google',
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': 'Paris'
            }, {
                'entreprise': 'Microsoft',
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': None
            }],
            columns=['entreprise', 'technologies',
                     'diplome', 'experience', 'ville']
        )
        self.predictions_with_missing_mandory_fields = pd.DataFrame(
            [{
                'entreprise': None,
                'technologies': None,
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': 'Paris'
            }, {
                'entreprise': 'Microsoft',
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': None,
                'experience': None,
                'ville': None
            }],
            columns=['entreprise', 'technologies',
                     'diplome', 'experience', 'ville']
        )
        self.client = TestClient(app)

    def test_read_predictions(self):
        """Test read predictions"""
        response = self.client.get('/predictions/')
        assert response.status_code == 200

    def test_create_prediction(self):
        """Test create prediction"""
        response = self.client.post(
            '/predict-profile/',
            json={
                'entreprise': 'Google',
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': 'Paris'
            }
        )
        assert response.status_code == 200
        assert response.json()['metier'] == 'Data architecte'

    def test_create_prediction_missing_fields(self):
        """Test create prediction missing fields"""
        response = self.client.post(
            '/predict-profile/',
            json={
                'technologies': 'Python, Sklearn, Pandas',
                'diplome': 'Bachelor',
                'experience': '1.5',
                'ville': 'Paris'
            }
        )
        assert response.status_code == 200
        assert response.json()['metier'] == 'Data architecte'

    def test_create_prediction_missing_mandaory_fields(self):
        """Test create prediction missing mandatory fields"""
        response = self.client.post(
            '/predict-profile/',
            json={
                'entreprise': 'Google',
                'experience': '1.5',
                'ville': 'Paris'
            }
        )
        assert response.status_code == 422

    def test_create_predictions(self):
        """Test create predictions"""
        response = self.client.post(
            '/predict-profiles/',
            files={'file': self.predictions.to_csv(sep=';')}
        )
        print(response.json())
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_create_predictions_missing_fields(self):
        """Test create predictions missing fields"""
        response = self.client.post(
            '/predict-profiles/',
            files={
                'file': self.predictions_with_missing_fields.to_csv(sep=';')}
        )
        print(response.json())
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_create_predictions_missing_mandaory_fields(self):
        """Test create predictions missing mandatory fields"""
        response = self.client.post(
            '/predict-profiles/',
            files={
                'file': self.predictions_with_missing_mandory_fields.to_csv(sep=';')}
        )
        assert response.status_code == 400
