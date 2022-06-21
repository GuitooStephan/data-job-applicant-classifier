import os
import glob
import datetime
import logging
import requests
import pandas as pd
import great_expectations as ge
from pathlib import Path
from dotenv import load_dotenv
import sendgrid
from sendgrid.helpers.mail import (
    Email, Mail, Personalization, Content
)
from airflow import AirflowException
from pendulum import now
from airflow.decorators import dag, task


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
}

DAGS_FOLDER = os.path.join(Path.cwd(), 'dags')
DATA_FOLDER = os.path.join(DAGS_FOLDER, 'data')


@dag(
    schedule_interval="*/2 * * * *",
    start_date=now().add(minutes=-10),
    dag_id='prediction_job',
    dagrun_timeout=datetime.timedelta(minutes=60),
    default_args=default_args
)
def make_predictions_pipeline():
    @task(
        task_id='make_prediction'
    )
    def make_prediction_with_newest_file(dependency):
        logger = logging.getLogger("console")

        newest_file = get_newest_file(
            os.path.join(DATA_FOLDER, 'cleaned_data'))
        logger.info(f"making prediction with file {newest_file}")

        send_file_to_api(newest_file)

        return newest_file

    @task(
        task_id='validate_source_data'
    )
    def validate_source_data():
        logger = logging.getLogger("console")

        # Get the newest file
        newest_file = get_newest_file(os.path.join(DATA_FOLDER, 'new_data'))
        logger.info(f"newest file: {newest_file}")

        df = pd.read_csv(
            newest_file,
            sep=';'
        )

        df.columns = map(str.lower, df.columns)

        ge_df = ge.from_pandas(df)
        result = ge_df.validate(
            expectation_suite=os.path.join(
                DAGS_FOLDER, 'suites', 'validation_suite.json')
        )

        if not result['success']:
            send_email(
                f"""Validation failed! \nFile: {newest_file} \nTime:
                {datetime.datetime.now()}\n{result['results']}"""
            )
            raise AirflowException(f"{newest_file} is not clean")

        logger.info(f"{newest_file} is clean")

        df.to_csv(
            os.path.join(DATA_FOLDER, 'cleaned_data',
                         os.path.basename(newest_file)),
            sep=';'
        )

        return result['success']

    make_prediction_with_newest_file(validate_source_data())


dag = make_predictions_pipeline()


####
def send_file_to_api(f):
    logger = logging.getLogger("console")
    response = requests.post(
        'http://localhost:8000/predict-profiles/',
        files={'file': open(f, 'rb')}
    )
    if response.status_code != 200:
        logger.error(f"{response.status_code}")
        logger.error(f"{response.json()}")
        raise AirflowException(f"{response.status_code}")
    logger.info(f"{response.status_code}")
    logger.info(f"{response.json()}")


def get_newest_file(folder):
    """
    Get the newest file in a folder
        @param folder: the folder to search
    """
    files = glob.glob(os.path.join(folder, '*.csv'))
    return max(files, key=os.path.getctime)


def send_email(body):
    """
    Send an email with the summary of the failed validation
        @param body: the body of the email
    """
    logger = logging.getLogger("console")
    load_dotenv(os.path.join(Path.cwd(), '.env'))

    logger.info(f"{os.environ.get('SENDGRID_API_KEY')}")

    sg = sendgrid.SendGridAPIClient(
        api_key=os.environ.get('SENDGRID_API_KEY')
    )

    from_email = Email(email=os.environ.get('SENDGRID_FROM_EMAIL'))
    recipient = Personalization()
    recipient.add_to(Email(email=os.environ.get('SENDGRID_TO_EMAIL')))

    mail = Mail(
        from_email, subject='Prediction Job Failed',
        plain_text_content=Content(mime_type='text/plain', content=body)
    )
    mail.add_personalization(recipient)

    response = sg.send(mail)
    logger.info(f"Email sent! Status code: {response.status_code}")
    return response.status_code
