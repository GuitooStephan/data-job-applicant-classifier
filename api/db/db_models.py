from db.database import Base
from sqlalchemy.sql import func
from sqlalchemy import (
    String,
    Integer,
    Float,
    Column,
    DateTime
)


class Profile(Base):
    __tablename__ = 'profile_classification'
    id = Column(Integer, primary_key=True, index=True)
    entreprise = Column(String(255), nullable=True)
    technologies = Column(String(1000), nullable=False)
    diplome = Column(String(255), nullable=True)
    experience = Column(Float, nullable=True)
    ville = Column(String(255), nullable=True)
    metier = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"<Item name={self.entreprise} metier={self.metier}>"
