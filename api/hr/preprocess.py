import os
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from hr.transformers import (
    TransformExperienceColumn, CreateIndividualTechnologyColumns, 
    DropNotSelectedColumns
)

SELECTED_TECHNOLOGIES = [
    'ruby', 'windows', 'oracle', 'mysql', 'hadoop(hdfs)', 'nosq', 'redshift', 'pig', 'map-reduce', 'hbase',
    'yarn', 'postgresql', 'kafka', 'tableau', 'vertica', 'mariadb', 'hdfs', 'numpy', 'deep learning', 'ai', 'scoring',
    'matplotlib', 'pycharm', 'scikit-learn', 'tensorflow', 'teradata', 'anglais', 'big data', 'r', 'machine learning', 
    'microsoft azure', 'spss', 'excel', 'sas', 'vba', 'matlab', 'aws', 'gnu', 'linux'
]
SELECTED_FEATURES = [ *SELECTED_TECHNOLOGIES, 'Experience' ]
TARGET_FEATURE = 'Metier'

PIPELINE_FILENAME = 'pipeline.joblib'
TARGET_ENCODER_FILENAME = 'label_encoder.joblib'

def save_object(obj, filename):
    parent_of_current_working_dir = Path(os.path.abspath(os.getcwd())).parent
    file_path = os.path.join(parent_of_current_working_dir, 'models', filename)
    joblib.dump(obj, file_path)

def load_object(filename):
    parent_of_current_working_dir = Path(os.path.abspath(os.getcwd())).parent
    file_path = os.path.join(parent_of_current_working_dir, 'models', filename)
    obj = joblib.load(file_path)
    return obj

# This function is used to drop duplicated rows 
# and drop na values from the experience column.
def clean_raw_data(df):
    _df = df.drop_duplicates()
    _df = df.dropna(subset=['Experience'])
    return _df

def split_train_data_raw(data, target_feature):
    le = LabelEncoder()
    X = data.drop(target_feature, axis=1)
    y = le.fit_transform(data[target_feature])

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size = 0.25, random_state = 0)
    
    save_object(le, TARGET_ENCODER_FILENAME)
    return X_train, X_val, y_train, y_val

def predict(data):
    pipeline = load_object(PIPELINE_FILENAME)
    y_pred = pipeline.predict(data)
    return y_pred

def train_model(X, y):
    # Train
    pipe = Pipeline(
        steps=[
            ('experience_transformer', TransformExperienceColumn()),
            ('individual_technologies', CreateIndividualTechnologyColumns(SELECTED_TECHNOLOGIES)),
            ('drop_not_selected_columns', DropNotSelectedColumns(SELECTED_FEATURES)),
            ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
            ('classifier', RandomForestClassifier(
                n_estimators=52, class_weight={0: 1, 1: 1, 2: 1, 3: 3}, max_depth=12
            ))
        ]
    )
    pipe.fit(X, y)
    save_object(pipe, PIPELINE_FILENAME)
