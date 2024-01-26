from fastapi import APIRouter, Path, HTTPException, status, Request, Depends
from fastapi.templating import Jinja2Templates

from model import Todo, TodoItems

todo_router = APIRouter()

todo_list = []

templates = Jinja2Templates(directory="templates/")


@todo_router.post("/todo")
async def add_todo(request: Request, todo: Todo = Depends(Todo.as_form)):
    todo.id = len(todo_list) + 1
    todo_list.append(todo)
    return templates.TemplateResponse("todo.html",
                                      {
                                          "request": request,
                                          "todos": todo_list
                                      })


@todo_router.get("/todo", response_model=TodoItems)
async def retrieve_todo(request: Request):
    return templates.TemplateResponse("todo.html", {
        "request": request,
        "todos": todo_list
    })

