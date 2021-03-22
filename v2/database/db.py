import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database.models import Favorite
from database.models import Base


class Database:
    def __init__(self):
        self.user = os.environ.get('POSTGRES_USER')
        self.password = os.environ.get('POSTGRES_PASSWORD')
        self.host = os.environ.get('POSTGRES_HOST')
        self.port = os.environ.get('POSTGRES_PORT')
        self.db = os.environ.get('POSTGRES_DATABASE')

    def create_session(self):
        engine = create_engine(
            f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}',
            echo=True,
        )
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
