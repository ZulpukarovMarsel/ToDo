from fastapi import APIRouter, HTTPException, Request
from repositories.roles import RolesRepository
from schemas.roles import RoleAddSchema, RoleSchema

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(lambda: None)]
)


@router.get('/', response_model=list[RoleSchema])
async def get_roles(request: Request):
    db = request.state.db
    role_repo = RolesRepository(db)
    roles = await role_repo.get_all()
    return roles


@router.post('/', response_model=RoleSchema)
async def add_roles(request: Request, role: RoleAddSchema):
    db = request.state.db
    role_repo = RolesRepository(db)
    role_data = role.dict()
    role = await role_repo.create_data(role_data)
    return role
