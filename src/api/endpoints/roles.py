from fastapi import APIRouter, HTTPException, Request
from repositories.roles import RolesRepository
from schemas.roles import RoleAddSchema, RoleSchema, RoleUpdateSchema

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(lambda: None)]
)


@router.get(
        '/',
        response_model=list[RoleSchema],
        # responses={
        #         401: {"model": ErrorResponse},
        #         404: {"model": ErrorResponse},
        #         500: {"model": ErrorResponse},
        #     }
        )
async def get_roles(request: Request):
    db = request.state.db
    role_repo = RolesRepository(db)
    roles = await role_repo.get_all()
    return roles


@router.get('/{role_id}', response_model=RoleSchema)
async def get_role(request: Request, role_id: int):
    db = request.state.db
    role_repo = RolesRepository(db)
    role = await role_repo.get_data_by_id(role_id)
    return role


@router.post('/', response_model=RoleSchema)
async def add_role(request: Request, role: RoleAddSchema):
    db = request.state.db
    role_repo = RolesRepository(db)
    role_data = role.dict()
    role = await role_repo.create_data(role_data)
    return role


@router.patch('/{roles_id}', response_model=RoleSchema)
async def patch_role(request: Request, role_id: int, data: RoleUpdateSchema):
    db = request.state.db
    role_repo = RolesRepository(db)
    update_role = await role_repo.update_data(role_id, data.dict(exclude_unset=True))
    if not update_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return update_role


@router.delete('/{role_id}', response_model=RoleSchema)
async def delete_role(request: Request, role_id: int):
    db = request.state.db
    role_repo = RolesRepository(db)
    deleted_role = await role_repo.delete_data(role_id)
    if not deleted_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return deleted_role
