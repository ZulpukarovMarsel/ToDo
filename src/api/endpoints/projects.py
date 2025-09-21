from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import selectinload

from models.users import User
from models.tasks import Task
from repositories.projects import ProjectRepository, ProjectInvitationRepository
from schemas.projects import (
    ProjectCreateSchema, ProjectCreateResponseSchema, ProjectResponseSchema,
    ProjectsResponseSchema,
    AddedInviterSchema, InvitationResponseSchema
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(lambda: None)]
)


@router.get('/', response_model=list[ProjectsResponseSchema])
async def get_projects(request: Request):
    db = request.state.db
    project_repo = ProjectRepository(db)
    projects = await project_repo.get_all(
        selectinload(project_repo.model.owner).selectinload(User.roles),
        selectinload(project_repo.model.participating_users).selectinload(User.roles),
        selectinload(project_repo.model.tasks).options(
            selectinload(Task.performer),
            selectinload(Task.status),
            selectinload(Task.priority)
        )
    )
    return projects


@router.post('/', response_model=ProjectCreateResponseSchema)
async def create_project(request: Request, project: ProjectCreateSchema):
    db = request.state.db
    user = request.state.user
    if not user:
        raise HTTPException(status_code=500, detail="Вы не авторизованы")

    project_repo = ProjectRepository(db)
    project_data = project.dict()
    project_data['owner_id'] = user.id
    new_project = await project_repo.create_project(project_data)
    return new_project


@router.post("/invitations")
async def added_inviter(request: Request, data: AddedInviterSchema):
    db = request.state.db
    user = request.state.user
    if not user:
        raise HTTPException(status_code=500, detail="Вы не авторизованы")
    project_invitation_repo = ProjectInvitationRepository(db)
    project_invitation = await project_invitation_repo.create_project_invitation(
        project_id=data.project_id, invited_id=data.invited_id, inviter_id=user.id
    )
    if not project_invitation:
        raise HTTPException(status_code=404, detail="Project invitation not found")
    return project_invitation


@router.get("/invitations/received", response_model=list[InvitationResponseSchema])
async def get_received_invitations(request: Request):
    db = request.state.db
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    project_invitation_repo = ProjectInvitationRepository(db)
    project_invitations = await project_invitation_repo.get_received_invitations(
        user.id,
        selectinload(project_invitation_repo.model.project),
        selectinload(project_invitation_repo.model.invited).selectinload(User.roles),
        selectinload(project_invitation_repo.model.inviter).selectinload(User.roles),
    )
    return project_invitations


@router.post("/invitations/{invitation_id}/accept")
async def accept_invitation(request: Request, invitation_id: int):
    db = request.state.db
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    project_invitation_repo = ProjectInvitationRepository(db)
    try:
        invitation = await project_invitation_repo.accept_invitation(
            invitation_id=invitation_id, user_id=user.id
        )
        return invitation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при принятии приглашения: {str(e)}")


@router.post("/invitations/{invitation_id}/decline")
async def decline_invitation(request: Request, invitation_id: int):
    db = request.state.db
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    project_invitation_repo = ProjectInvitationRepository(db)
    try:
        invitation = await project_invitation_repo.decline_invitation(
            invitation_id=invitation_id, user_id=user.id
        )
        return invitation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при принятии приглашения: {str(e)}")


@router.get('/{project_id}', response_model=ProjectResponseSchema)
async def get_project(request: Request, project_id: int):
    db = request.state.db
    project_repo = ProjectRepository(db)
    project = await project_repo.get_data_by_id(
        project_id,
        selectinload(project_repo.model.owner).selectinload(User.roles),
        selectinload(project_repo.model.participating_users).selectinload(User.roles),
        selectinload(project_repo.model.tasks).options(
            selectinload(Task.performer),
            selectinload(Task.status),
            selectinload(Task.priority)
        )
    )
    if not project:
        raise HTTPException(status_code=400, detail="Проект с таким id не найден")
    return project


@router.delete('/{project_id}')
async def delete_project(request: Request, project_id: int):
    db = request.state.db
    project_repo = ProjectRepository(db)
    deleted_project = await project_repo.delete_data(project_id)
    if deleted_project:
        return deleted_project
        # return JSONResponse(content="Вы успешно удалили проект", status_code=200)
    raise HTTPException(status_code=500, detail="Проект с таким id не найден")
