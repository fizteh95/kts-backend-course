import copy
import enum
from dataclasses import dataclass
import typing
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class SessionStates(enum.Enum):
    checking_theme = 'checking_theme'
    answering = 'answering'
    finished = 'finished'


@dataclass
class Session:
    state: SessionStates = None
    last_text: str = ""
    last_state: SessionStates = None
    checked_theme: int = None
    checked_question: int = None
    last_checked_question: int = None
    score: int = 0
    last_score: int = 0


start_phrase = 'старт'
stop_phrase = 'стоп'
status_phrase = 'статус'


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def output_generator(self, user_id: int, session: Session, input_text: str) -> (Session, str):
        output_text = ""
        updated_session = copy.deepcopy(session)

        if status_phrase in input_text.lower():
            await self.app.store.vk_api.send_message(Message(user_id=user_id, text=f"Текущий счет: {session.score}"))
            session.state = updated_session.last_state
            session.checked_question = updated_session.last_checked_question
            session.score = updated_session.last_score
            updated_session, output_text = await self.output_generator(user_id, session, session.last_text)
            return updated_session, output_text

        if stop_phrase in input_text.lower():
            output_text = "Прерывание раунда, очень жаль("
            updated_session = Session()
        elif not session.state and input_text.lower() != start_phrase:
            output_text = "Введите \"Старт\" для начала игры."
        elif not session.state and input_text.lower() == start_phrase:
            themes = await self.app.store.quizzes.list_themes()
            main_text = "Для того, чтобы узнать статус текущего раунда введи \"Статус\", для сброса \
раунда введи \"Стоп\". Выбери интересующую тему вопросов:"
            texts = []
            for theme in themes:
                texts.append(f"{theme.id}. {theme.title}")
            await self.app.store.vk_api.send_keyboard(user_id, main_text, texts)
            updated_session.last_state = updated_session.state
            updated_session.state = SessionStates.checking_theme
        elif session.state == SessionStates.checking_theme:
            in_text = input_text.split('. ')[-1]
            theme = await self.app.store.quizzes.get_theme_by_title(in_text)
            if theme:
                updated_session.checked_theme = theme.id
                questions = await self.app.store.quizzes.list_questions(theme_id=theme.id)
                updated_session.checked_question = questions[0].id
                main_text = f"Начнем раунд! Первый вопрос: \n\r{questions[0].title}"
                texts = []
                for answer in questions[0].answers:
                    texts.append(f"{answer.title}")
                await self.app.store.vk_api.send_keyboard(user_id, main_text, texts)
                updated_session.last_state = updated_session.state
                updated_session.state = SessionStates.answering
        elif session.state == SessionStates.answering:
            in_text = input_text.split('] ')[-1]
            current_question = await self.app.store.quizzes.get_question_by_id(session.checked_question)
            if current_question:
                updated_session.last_score = updated_session.score
                for answer in current_question.answers:
                    if answer.is_correct and answer.title == in_text:
                        main_text = 'Верно!'
                        updated_session.score = session.score + 1
                        break
                else:
                    main_text = 'Неверно!'
                all_questions = await self.app.store.quizzes.list_questions(session.checked_theme)
                next_questions = [x for x in all_questions if x.id > session.checked_question]
                updated_session.last_checked_question = updated_session.checked_question
                if next_questions:
                    question = next_questions[0]
                    updated_session.checked_question = question.id
                    main_text += f" Следующий вопрос: \n\r{question.title}"
                    texts = []
                    for answer in question.answers:
                        texts.append(f"{answer.title}")
                    await self.app.store.vk_api.send_keyboard(user_id, main_text, texts)
                    updated_session.last_state = updated_session.state
                    updated_session.state = SessionStates.answering
                else:
                    main_text += f' Раунд закончен. Ваш счет: {updated_session.score}. Попробуем еще раз?'
                    texts = ['Да', 'Нет']
                    await self.app.store.vk_api.send_keyboard(user_id, main_text, texts)
                    updated_session.last_state = updated_session.state
                    updated_session.state = SessionStates.finished
        elif session.state == SessionStates.finished:
            if 'нет' in input_text.lower():
                output_text = 'Рады были поиграть! Приходи еще ;)'
                updated_session = Session()
            elif 'да' in input_text.lower():
                updated_session.last_score = updated_session.score
                updated_session.score = 0
                themes = await self.app.store.quizzes.list_themes()
                main_text = "Выбери интересующую тему вопросов:"
                texts = []
                for theme in themes:
                    texts.append(f"{theme.id}. {theme.title}")
                await self.app.store.vk_api.send_keyboard(user_id, main_text, texts)
                updated_session.last_state = updated_session.state
                updated_session.state = SessionStates.checking_theme
        updated_session.last_text = input_text
        return updated_session, output_text

    async def handle_updates(self, updates: list[Update]):
        if not updates:
            return
        for update in updates:
            session = await self.app.store.sessions.get_session(update.object.user_id)
            if not session:
                session = await self.app.store.sessions.create_session(update.object.user_id)
            updated_session, output_text = await self.output_generator(update.object.user_id,
                                                                       session,
                                                                       update.object.body)
            await self.app.store.sessions.write_session(update.object.user_id, updated_session)
            if output_text:
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.user_id,
                        text=output_text,
                    )
                )
