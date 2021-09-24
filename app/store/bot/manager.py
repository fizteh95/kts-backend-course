from dataclasses import dataclass
import typing
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class Session:
    state: str
    last_check: str

session_store = {}  # user -> session

start_phrase = 'старт'

async def output_generator(app: "Application", session: Session, input_text: str) -> (Session, str):
    output_text = ""
    updated_session = Session(state="", last_check="")
    if not session.state and input_text.lower() != start_phrase:
        output_text = 'Введите "Старт" для начала игры.'
    elif not session.state and input_text.lower() == start_phrase:
        themes = await app.store.quizzes.list_themes()
        output_text = "Введите номер или название интересующей темы вопросов:\n\r"
        for theme in themes:
            output_text += f"{theme.id}. {theme.title}"
        updated_session.state = "checking_theme"
    elif session.state == "checking_theme":
        try:
            theme_id = int(input_text)
        except ValueError:
            theme = app.store.quizzes.get_theme_by_title(input_text)
            theme_id = theme.id
    return updated_session, output_text


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        if not updates:
            return
        for update in updates:
            session = session_store.get(update.object.user_id, Session(state="", last_check=""))
            updated_session, output_text = await output_generator(self.app, session, update.object.body)
            session_store[update.object.user_id] = updated_session
            await self.app.store.vk_api.send_message(
                Message(
                    user_id=update.object.user_id,
                    text=output_text,
                )
            )
