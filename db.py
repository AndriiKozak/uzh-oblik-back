from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Boolean, Integer, DateTime, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_keyed_dict
from dataclasses import dataclass, asdict
from sqlalchemy.dialects.postgresql import ARRAY

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
ranks = ("Головний майстер-сержант",	"Старший майстер-сержант",	"Майстер-сержант",	"Штаб-сержант",	"Головний сержант",	"Старший сержант",	"Сержант",	"Молодший сержант",	"Старший солдат",	"Солдат",	"Рекрут")
officer_ranks = ("Генерал", 	"Генерал-лейтенант",	"Генерал-майор",	"Бригадний генерал", 	"Полковник", 	"Підполковник", 	"Майор",	"Капітан", 	"Старший лейтенант",	"Лейтенант",	"Молодший лейтенант",	"Курсант")
sex = ("Чоловік", "Жінка")
DBRank = Integer
Gender = bool
DBGender = Boolean

class DbUser(db.Model):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    hash: Mapped[str] = mapped_column(String)
    is_admin: Mapped[Boolean] = mapped_column(Boolean)


@dataclass
class Item(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    returnable: Mapped[bool] = mapped_column(Boolean)

    def to_dict(self):
        return asdict(self)


@dataclass
class Norm(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    genders: Mapped[list[Gender]] = mapped_column(ARRAY(DBGender))
    # ranks: Mapped[list[int]] = mapped_column(ARRAY(DBRank))
    from_rank: Mapped[int] = mapped_column(Integer)
    to_rank:  Mapped[int] = mapped_column(Integer)
    obligations = relationship("Obligation", backref="norm")
    name: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    from_date: Mapped[datetime] = mapped_column(DateTime)
    to_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        return asdict(self)


class Obligation(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group: Mapped[str] = mapped_column(String)
    item_id = Column(Integer, ForeignKey(Item.id))
    item = relationship(Item)
    term:  Mapped[int] = mapped_column(Integer)
    norm_id = Column(Integer, ForeignKey(Norm.id))
    count: Mapped[int] = mapped_column(Integer)


@dataclass
class Serviceman(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    patronymic: Mapped[str] = mapped_column(String)
    issues = relationship("Issue", backref="serviceman")
    rank_history: Mapped[list[datetime]] = mapped_column(ARRAY(DateTime)) # Array of date, rank starts. None if not started
    gender: Mapped[Gender] = mapped_column(DBGender)
    group: Mapped[str] = mapped_column(String)
    sizes: Mapped[dict[int, 'Size']] = relationship(
        collection_class=attribute_keyed_dict("item_id"),
    )

    def get_ranks(self):
        ranks = []
        for i in range(len(self.rank_history)-1):
            if self.rank_history[i+1] - self.rank_history[i] > timedelta(days=1):
                ranks.append(i)
        ranks.append(len(self.rank_history)-1)
        return ranks

    def to_dict(self):
        d = asdict(self)
        d["rank"] = len(d["rank_history"]) - 1
        del d["rank_history"]
        d["issues"] = [issue.to_dict() for issue in self.issues]
        return d


@dataclass()
class Size(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey(Item.id))
    item = relationship(Item)
    size: Mapped[str] = mapped_column(String)
    serviceman_id = mapped_column(Integer, ForeignKey(Serviceman.id))

@dataclass()
class Issue(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey(Item.id))
    item = relationship(Item)
    serviceman_id = Column(Integer, ForeignKey(Serviceman.id))
    size: Mapped[str] = mapped_column(String)
    granted: Mapped[datetime] = mapped_column(DateTime)
    date: Mapped[datetime] = mapped_column(DateTime)
    count: Mapped[int] = mapped_column(Integer)

    def to_dict(self):
        d = asdict(self)
        d["date"] = d.get("date").strftime("%d.%m.%Y")
        d["item"] = self.item.to_dict()
        d["granted"] = d.get("granted").strftime("%d.%m.%Y")
        return d
@dataclass()
class ServicemanObligation:
    item: Item
    size: str
    count: int
    date: datetime
    term: int
