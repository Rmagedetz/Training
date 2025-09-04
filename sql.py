import datetime
import pandas as pd
from sqlalchemy import (Column, Integer, BigInteger, String, Date, Float, create_engine, DateTime,
                        UniqueConstraint, delete, func, text, Numeric)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from connections import sql_connection_string

engine = create_engine(sql_connection_string)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Exercises(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    exercise_group = Column(String(50))
    exercise_name = Column(String(100))

    @classmethod
    def get_list_works(cls):
        with session_scope() as session:
            return [row[0] for row in session.query(cls.exercise_name).distinct().order_by(cls.exercise_name).all()]

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), nullable=False)
    user_tg_id = Column(BigInteger, unique=True, nullable=False)

    @classmethod
    def get_list(cls):
        with session_scope() as session:
            return [row[0] for row in session.query(cls.username).distinct().order_by(cls.username).all()]

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def get_name(cls, tg_id):
        with session_scope() as session:
            user = session.query(cls).filter(cls.user_tg_id == tg_id).first()
            return user.username if user else None


class Plan(Base):
    __tablename__ = "plan"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    username = Column(String(30))
    exercise_name = Column(String(100))
    weight_steps_repeats = Column(String(100))

    @classmethod
    def get_by_date(cls, date_str: str, username: str) -> str:
        target_date = datetime.datetime.strptime(date_str, "%d.%m.%y").date()

        with session_scope() as session:
            records = session.query(cls).filter(cls.date == target_date,
                                                cls.username == username).all()
            if not records:
                return f"На {date_str} упражнений не найдено."

            lines = [
                f"{i + 1}. {r.exercise_name}: {r.weight_steps_repeats}"
                for i, r in enumerate(records)
            ]
            return "\n".join(lines)

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(**parameters).delete()
            session.commit()

    @classmethod
    def get_df(cls, **parameters):
        with session_scope() as session:
            try:
                columns = [c.name for c in cls.__table__.columns]
                query = session.query(*[getattr(cls, col) for col in columns]).filter_by(**parameters)
                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()


Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    finally:
        db.close()
