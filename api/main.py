import os
import uvicorn
import pandas as pd
import great_expectations as ge
from pathlib import Path
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from data_profile_classifier.inference import make_predictions
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from db import crud, db_models, database, schemas
from fastapi_pagination import Page, Params, paginate

RESOURCES_PATH = os.path.join(Path.cwd(), 'resources')

app = FastAPI(
    title='HR Data Engineer Classifier',
    version='1.0',
    description=''
)

# Load .env file
load_dotenv('./.env')
# Load database engine
db_models.Base.metadata.create_all(bind=database.engine)


def get_db():
    """Load database session"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def home():
    return {'message': 'Thank you for using our hr classifier API'}


@app.post(
    "/predict-profiles/"
)
def predict_profiles(file: UploadFile, db: Session = Depends(get_db)):
    """Predict profiles from a csv file"""
    user_data_df = pd.read_csv(file.file, sep=';')
    user_data_df.columns = map(str.lower, user_data_df.columns)

    if user_data_df.empty:
        raise HTTPException(status_code=400, detail="Bad request")

    ge_df = ge.from_pandas(user_data_df)
    validation_result = ge_df.validate(
        expectation_suite=os.path.join(
            RESOURCES_PATH, 'validation_suite.json'
        )
    )

    if not validation_result['success']:
        raise HTTPException(
            status_code=400, detail="Bad request - Data not clean")

    user_data_df.columns = map(str.capitalize, user_data_df.columns)
    predictions = make_predictions(
        user_data_df,
        os.environ.get(
            'MODELS_DIR'
        )
    )
    user_data_df['Metier'] = predictions

    results = crud.create_profile_classifications(db, user_data_df)

    return results


@app.post("/predict-profile/")
def predict_profile(prediction: schemas.ProfileInput, db: Session = Depends(get_db)):
    """Predict a profile"""
    user_data_df = pd.DataFrame(
        [{
            'Entreprise': prediction.entreprise,
            'Technologies': prediction.technologies,
            'Diplome': prediction.diplome,
            'Experience': prediction.experience,
            'Ville': prediction.ville
        }]
    )

    predictions = make_predictions(
        user_data_df,
        os.environ.get(
            'MODELS_DIR'
        )
    )
    user_data_df['Metier'] = predictions

    results = crud.create_profile_classification(db, user_data_df)

    return results


@app.get(
    '/predictions/',
    response_model=Page[schemas.Profile]
)
def get_all_profile_predictions(
    db: Session = Depends(get_db),
    params: Params = Depends()
):
    classifications = crud.get_profile_classifications(db)

    return paginate(classifications, params)


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
