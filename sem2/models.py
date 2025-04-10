# project/app/db/models.py
from sqlalchemy.ext.declarative import declarative_base

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
