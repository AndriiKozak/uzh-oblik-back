import dataclasses

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from dataclasses import dataclass, asdict

class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)


class DbUser(db.Model):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    hash: Mapped[str] = mapped_column(String)
    is_admin: Mapped[Boolean] = mapped_column(Boolean)


class Item(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    returnable: Mapped[bool] = mapped_column(Boolean)
    #TODO something reasonble Timedelta
    term: Mapped[float] = mapped_column(Float)

@dataclass
class Serviceman(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    patronymic: Mapped[str] = mapped_column(String)

    def to_dict(self):
        return asdict(self)

