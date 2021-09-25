import typing
from hashlib import sha256
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin, AdminModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)
        await self.create_admin(
            email=app.config.admin.email, password=app.config.admin.password
        )

    async def disconnect(self, app: "Application"):
        await AdminModel.delete.gino.all()

    async def get_by_email(self, email: str) -> Optional[Admin]:
        admin = await AdminModel.query.where(AdminModel.email == email).gino.first()
        if admin:
            return Admin(id=admin.id, email=admin.email, password=sha256(admin.password.encode()).hexdigest())

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = await AdminModel.create(email=email, password=password)
        return admin
