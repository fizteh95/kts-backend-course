import json

from app.base.base_accessor import BaseAccessor
from app.bot.models import SessionModel
from app.store.bot.manager import Session
from app.store.bot.manager import SessionStates


class SessionAccessor(BaseAccessor):
    async def create_session(self, client: int) -> Session:
        session = await SessionModel.create(client=client)
        return Session()

    async def get_session(self, client: int) -> Session:
        session = await SessionModel.query.where(SessionModel.client == client).gino.first()
        if session:
            session_loaded = json.loads(session.session)
            state = session_loaded.get('state')
            if state:
                state = SessionStates(state)
            last_text = session_loaded.get('last_text')
            last_state = session_loaded.get('last_state')
            if last_state:
                last_state = SessionStates(last_state)
            checked_theme = session_loaded.get('checked_theme')
            checked_question = session_loaded.get('checked_question')
            last_checked_question = session_loaded.get('last_checked_question')
            score = session_loaded.get('score')
            last_score = session_loaded.get('last_score')
            session = Session(state=state,
                              last_text=last_text,
                              last_state=last_state,
                              checked_theme=checked_theme,
                              checked_question=checked_question,
                              last_checked_question=last_checked_question,
                              score=score,
                              last_score=last_score)
        return session

    async def write_session(self, client: int, session: Session) -> Session:
        db_session = await SessionModel.query.where(SessionModel.client == client).gino.first()
        state = None
        last_state = None
        if session.state:
            state = session.state.value
        if session.last_state:
            last_state = session.last_state.value
        session_dumped = json.dumps(dict(
            state=state,
            last_text=session.last_text,
            last_state=last_state,
            checked_theme=session.checked_theme,
            checked_question=session.checked_question,
            last_checked_question=session.last_checked_question,
            score=session.score,
            last_score=session.last_score
        ))
        await db_session.update(session=session_dumped).apply()
        return session

