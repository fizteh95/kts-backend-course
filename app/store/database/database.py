from gino.api import Gino
from app.store.database.gino import db
from app.admin.models import *
from app.quiz.models import *
from app.bot.models import *
from sqlalchemy.engine.url import URL


class Database:
    db: Gino

    def __init__(self, app: "Application"):
        self.app = app
        self.db: Optional[Gino] = None

    async def connect(self, *_, **kw):
        self.db = db
        self._engine = await self.db.set_bind(
            URL(
                drivername="asyncpg",
                host=self.app.config.database.host,
                database=self.app.config.database.database,
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                port=self.app.config.database.port,
            ),
            min_size=1,
            max_size=1,
        )
        self.db.bind = self._engine

    async def disconnect(self, *_, **kw):
        # if self.db:
        #     await self.db.bind.close()
        print('database disconnected')

