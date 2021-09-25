from collections import defaultdict
from typing import Optional

from asyncpg.exceptions import ForeignKeyViolationError

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Theme,
    Question,
    Answer,
    ThemeModel,
    QuestionModel,
    AnswerModel,
)
from typing import List


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        theme = await ThemeModel.create(title=title)
        theme = Theme(id=theme.id, title=theme.title)
        return theme

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        theme = await ThemeModel.query.where(ThemeModel.title == title).gino.first()
        if theme:
            theme = Theme(id=theme.id, title=theme.title)
        return theme

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        theme = await ThemeModel.query.where(ThemeModel.id == id_).gino.first()
        if theme:
            theme = Theme(id=theme.id, title=theme.title)
        return theme

    async def list_themes(self) -> List[Theme]:
        themes = await ThemeModel.query.gino.all()
        res = []
        for theme in themes:
            res.append(Theme(id=theme.id, title=theme.title))
        return res

    async def delete_theme_by_title(self, title: str) -> None:
        theme = await self.get_theme_by_title(title)
        await ThemeModel.delete.where(ThemeModel.title == title).gino.status()
        return theme

    async def create_answers(self, question_id, answers: List[Answer]):
        for answer in answers:
            await AnswerModel.create(question_ref=question_id, title=answer.title, is_correct=answer.is_correct)

    async def create_question(self, title: str, theme_id: int, answers: List[Answer]) -> Question:
        question = await QuestionModel.create(title=title, theme_id=theme_id, theme_ref=theme_id)
        await self.create_answers(question_id=question.id, answers=answers)
        question = Question(id=question.id, title=question.title, theme_id=question.theme_id, answers=answers)
        return question

    async def delete_question_by_title(self, title: str) -> Optional[Question]:
        question = await self.get_question_by_title(title)
        await QuestionModel.delete.where(QuestionModel.title == title).gino.status()
        return question

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        question = await (
            QuestionModel
            .join(AnswerModel, QuestionModel.id == AnswerModel.question_ref)
            .select()
            .where(QuestionModel.title == title)
            .gino
            .load(QuestionModel.load(answers=AnswerModel))
            .all()
        )
        res = None
        if question:
            q = question[0]
            res = Question(id=q.id, theme_id=q.theme_id, title=q.title, answers=[])
            for a in question:
                res.answers.append(Answer(title=a.answers[0].title, is_correct=a.answers[0].is_correct))
        return res

    async def get_question_by_id(self, id_: int) -> Optional[Question]:
        question = await (
            QuestionModel
            .join(AnswerModel, QuestionModel.id == AnswerModel.question_ref)
            .select()
            .where(QuestionModel.id == id_)
            .gino
            .load(QuestionModel.load(answers=AnswerModel))
            .all()
        )
        res = None
        if question:
            q = question[0]
            res = Question(id=q.id, theme_id=q.theme_id, title=q.title, answers=[])
            for a in question:
                res.answers.append(Answer(title=a.answers[0].title, is_correct=a.answers[0].is_correct))
        return res

    async def list_questions(self, theme_id: Optional[int] = None) -> List[Question]:
        questions = defaultdict(Question)
        answers = defaultdict(list)
        if not theme_id:
            db_questions = await (
                QuestionModel
                .outerjoin(AnswerModel, QuestionModel.id == AnswerModel.question_ref)
                .select()
                .gino
                .load(QuestionModel.load(answers=AnswerModel))
                .all()
            )
        else:
            db_questions = await (
                QuestionModel
                .outerjoin(AnswerModel, QuestionModel.id == AnswerModel.question_ref)
                .select()
                .where(QuestionModel.theme_id == theme_id)
                .gino
                .load(QuestionModel.load(answers=AnswerModel))
                .all()
            )
        for question in db_questions:
            questions[question.title] = Question(id=question.id,
                                                 theme_id=question.theme_id,
                                                 title=question.title,
                                                 answers=[])
            a = question.answers[0]
            answers[question.title] += [Answer(title=a.title, is_correct=a.is_correct)]
        res = []
        for question in questions.values():
            res.append(question)
            res[-1].answers = answers[question.title]
        res.sort(key=lambda x: x.id)
        return res
