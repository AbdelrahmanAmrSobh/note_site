import os

from dotenv import load_dotenv
from sqlmodel import create_engine, select, Session, SQLModel

from models.note import Note, NoteUserLink
from models.session import UserSession
from models.user import User

load_dotenv()

DB_TYPE = os.environ["DB_TYPE"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_SERVER = os.environ["DB_SERVER"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

DB_URL = f"{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

classes = {
    "note": Note,
    "link": NoteUserLink,
    "user": User,
    "session": UserSession,
}


def get_cls(cls):
    if hasattr(cls, "value"):
        cls = cls.value
    if type(cls) is str:
        cls = classes.get(cls.lower())
    if cls:
        return cls
    print(
        f"Invalid or not supported class, supported classes are {classes.keys()}")
    raise TypeError("Invalid or not supported class")


class DBStorage:

    __engine = None
    __session = None

    def __init__(self):
        self.__engine = create_engine(DB_URL)

    def reload(self):
        Note.model_rebuild()
        NoteUserLink.model_rebuild()
        User.model_rebuild()
        UserSession.model_rebuild()
        # Create all tables in the database
        SQLModel.metadata.create_all(self.__engine)

    def _get_session(self):
        if self.__session is None:
            self.__session = Session(self.__engine)
        return self.__session

    def new(self, obj):
        session = self._get_session()
        session.add(obj)

    def delete(self, obj):
        session = self._get_session()
        session.delete(obj)

    def save(self):
        session = self._get_session()
        session.commit()

    def close(self):
        if self.__session:
            self.__session.close()
            self.__session = None

    def get(self, cls, **kwargs):
        session = self._get_session()
        cls = get_cls(cls)
        if not kwargs or not cls:
            return None
        statement = select(cls)
        for attr, value in kwargs.items():
            if value:
                statement = statement.where(getattr(cls, attr) == value)
        items = list(session.exec(statement).all())
        if len(items) == 1:
            return items[0]
        return None

    def all(self, cls, **kwargs):
        session = self._get_session()
        cls = get_cls(cls)
        statement = select(cls)
        for attr, value in kwargs.items():
            if value:
                statement = statement.where(getattr(cls, attr) == value)
        return session.exec(statement).all()
