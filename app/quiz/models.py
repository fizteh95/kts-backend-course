from dataclasses import dataclass
from typing import Optional

from app.store.database.gino import db


@dataclass
class Theme:
    id: Optional[int]
    title: str


# TODO
# Дописать все необходимые поля модели
class ThemeModel(db.Model):
    __tablename__ = "themes"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False, unique=True)


# TODO
# Дописать все необходимые поля модели
class AnswerModel(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    title = db.Column(db.String(), nullable=False)  # primary_key=True,
    is_correct = db.Column(db.Boolean(), nullable=False)
    question_ref = db.Column(db.ForeignKey('questions.id', ondelete="CASCADE"), nullable=False)


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]


# TODO
# Дописать все необходимые поля модели
class QuestionModel(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False, unique=True)
    theme_id = db.Column(db.Integer(), nullable=False)
    theme_ref = db.Column(db.ForeignKey('themes.id', ondelete="CASCADE"), nullable=False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._answers: list[AnswerModel] = list()

    @property
    def answers(self) -> list[AnswerModel]:
        return self._answers

    @answers.setter
    def answers(self, value: Optional[AnswerModel]):
        if value is not None:
            self._answers.append(value)


@dataclass
class Answer:
    title: str
    is_correct: bool
