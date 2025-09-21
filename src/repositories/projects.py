from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base_repository import BaseRepository
from .users import UserRepository
from schemas.projects import InvitationStatus
from models.projects import Project, ProjectInvitation
from services.base_service import BaseService


class ProjectRepository(BaseRepository):
    model = Project

    async def create_project(self, project_data: dict):
        user_repo = UserRepository(self.db)
        owner = await user_repo.get_data_by_id(project_data['owner_id'])
        if not owner:
            raise ValueError(f"Owner with id {project_data['owner_id']} not found")

        project = self.model(
            title=project_data['title'],
            owner_id=project_data['owner_id']
            )

        self.db.add(project)
        try:
            await self.db.commit()
            await self.db.refresh(project)
            return project
        except Exception as e:
            await self.db.rollback()
            raise e


class ProjectInvitationRepository(BaseRepository):
    model = ProjectInvitation

    async def create_project_invitation(self, project_id: int, invited_id: int, inviter_id: int):
        user_repo = UserRepository(self.db)
        project_repo = ProjectRepository(self.db)

        project = await project_repo.get_data_by_id(project_id)
        if not project or project.owner_id != inviter_id:
            raise ValueError("Проект с таким id не существует")
        invited = await user_repo.get_data_by_id(invited_id)
        if not invited:
            raise ValueError("Пользовател с таким id не существует")
        inviter = await user_repo.get_data_by_id(inviter_id)
        if not inviter:
            raise ValueError("Пользовател с таким id не существует")

        project_invitation = self.model(
            project_id=project_id,
            invited_id=invited_id,
            inviter_id=inviter_id
        )
        self.db.add(project_invitation)
        message = f"""
                <!DOCTYPE html>
                <html>
                    <body>
                        <p>Вас позвал {inviter.full_name()} в проект {project.title}</p>
                    </body>
                </html>
            """
        try:
            await self.db.commit()
            await self.db.refresh(project_invitation)
            send_message = await BaseService.send_message_to_email([invited.email], message)
            if not send_message:
                raise ValueError("Сервер не смог отправить увидомление")
            return project_invitation
        except Exception as e:
            await self.db.rollback()
            return e

    async def get_received_invitations(self, invited_id: int, *options):
        stmt = select(self.model).where(self.model.invited_id == invited_id)
        if options:
            stmt = stmt.options(*options)
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_my_sent_invitations(self, inviter_id: int, *options):
        stmt = select(self.model).where(self.model.inviter_id == inviter_id)
        if options:
            stmt = stmt.options(*options)
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def accept_invitation(self, invitation_id: int, user_id: int):
        try:
            invitation = await self.get_data_by_id(
                invitation_id,
                selectinload(self.model.project).selectinload(Project.participating_users)
            )

            if not invitation:
                raise ValueError("Приглашение не найдено")

            if invitation.invited_id != user_id:
                raise ValueError("Это приглашение не предназначено вам")

            if invitation.status != InvitationStatus.PENDING:
                raise ValueError("Приглашение уже обработано")

            project_repo = ProjectRepository(self.db)
            user_repo = UserRepository(self.db)

            project = await project_repo.get_data_by_id(invitation.project_id)
            user = await user_repo.get_data_by_id(user_id)

            if not project:
                raise ValueError("Проект не найден")

            if not user:
                raise ValueError("Пользователь не найден")

            existing_participants = [p.id for p in project.participating_users]
            if user_id not in existing_participants:
                project.participating_users.append(user)

            invitation.status = InvitationStatus.ACCEPTED

            await self.db.commit()
            await self.db.refresh(invitation)
            await self.db.refresh(project)
            return invitation

        except Exception as e:
            await self.db.rollback()
            raise e

    async def decline_invitation(self, invitation_id: int, user_id: int):
        invitation = await self.get_data_by_id(invitation_id)
        if not invitation:
            raise ValueError("Приглашение не найдено")
        if invitation.invited_id != user_id:
            raise ValueError("Это приглашение не предназначено вам")
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Приглашение уже обработано")
        invitation.status = InvitationStatus.DECLINED
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation
