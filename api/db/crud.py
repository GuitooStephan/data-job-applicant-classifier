import math
import pandas as pd
from sqlalchemy import desc
from sqlalchemy.orm import Session
import db.db_models as db_models


def create_profile_classifications(
    db: Session,
    df: pd.DataFrame
):
    """
    Create new profile classifications from a dataframe
        @param db: Session object to the database
        @param df: Dataframe with the data to create the profile classifications
    """
    profiles = []

    for i in range(len(df)):
        profiles.append(
            parse_df_row(df.iloc[i])
        )

    db.bulk_save_objects(profiles, return_defaults=True)
    db.commit()

    return profiles


def create_profile_classification(
    db: Session,
    df: pd.DataFrame
):
    """
    Create new profile classification from a dataframe
        @param db: Session object to the database
        @param df: Dataframe with the data to create the profile classification
    """
    new_pred = parse_df_row(df.iloc[0])
    db.add(new_pred)
    db.commit()

    db.refresh(new_pred)

    return new_pred


def get_profile_classifications(db: Session):
    """
    Get all profile classifications
        @param db: Session object to the database
    """
    return db.query(
        db_models.Profile
    ).order_by(
        desc(db_models.Profile.created_at)
    ).all()


def parse_df_row(row):
    """
    Parse a dataframe row to a profile classification model
    """
    return db_models.Profile(
        entreprise=row['Entreprise'] if not pd.isna(
            row['Entreprise']) else None,
        technologies=row['Technologies'],
        diplome=row['Diplome'] if not pd.isna(row['Diplome']) else None,
        experience=float(str(row['Experience']).replace(',', '.')),
        ville=row['Ville'] if not pd.isna(row['Ville']) else None,
        metier=row['Metier']
    )
