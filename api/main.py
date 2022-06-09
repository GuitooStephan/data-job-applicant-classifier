import uvicorn
import pandas as pd
from fastapi import FastAPI, UploadFile, Request
from pydantic import BaseModel
from typing import Union
from hr.inference import make_predictions

app = FastAPI(
    title='HR Data Engineer Classifier',
    version='1.0',
    description=''
)

@app.get('/')
def home():
    return {'message': 'Thank you for using our hr classifier API'}

@app.post("/predict-file/")
def predict(csv_file: UploadFile):
    user_data_df = pd.read_csv(csv_file.file, sep=';')

    if user_data_df.empty:
        return {'status': 400, 'message': "Bad request"}

    if not set([
        'Entreprise','Metier', 'Technologies', 'Diplome',
        'Experience', 'Ville']
        ).issubset(user_data_df.columns) :
        return {'status': 400, 'message': "Bad request - Columns missing"}

    predictions = make_predictions(user_data_df)
    user_data_df['Metier'] = predictions

    return {'status': 200,
            'message': "Successful",
            'results': user_data_df.values.tolist()}


class Prediction(BaseModel):
    Entreprise: str
    Metier: Union[str, None] = None
    Technologies: str
    Diplome: str
    Experience: str
    Ville: str

@app.post("/predict/")
def predict(prediction:Prediction):
    user_data_df = pd.DataFrame(
        [{
            'Entreprise': prediction.Entreprise,
            'Metier': prediction.Metier,
            'Technologies': prediction.Technologies,
            'Diplome': prediction.Diplome,
            'Experience': prediction.Experience,
            'Ville': prediction.Ville
        }]
    )

    predictions = make_predictions(user_data_df)
    user_data_df['Metier'] = predictions

    return {'status': 200,
            'message': "Successful",
            'results': user_data_df.values.tolist()}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
