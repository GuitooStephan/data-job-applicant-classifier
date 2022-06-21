from typing import Union
from pydantic import BaseModel
import datetime


class Profile(BaseModel):
    id: int
    entreprise: Union[str, None] = None
    technologies: str
    diplome: Union[str, None] = None
    experience: float
    ville: Union[str, None] = None
    metier: Union[str, None] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class ProfileInput(BaseModel):
    entreprise: Union[str, None] = None
    technologies: str
    diplome: Union[str, None] = None
    experience: str
    ville: Union[str, None] = None
