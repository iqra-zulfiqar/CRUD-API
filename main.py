from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.requests import Request
from pydantic import BaseModel, field_validator

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A tiny in-memory CRUD API for managing a to-do list.",
)

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write README", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]
next_id = 4

class TaskCreate(BaseModel):
    title: str
    done: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

class TaskUpdate(TaskCreate):
    pass

def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)

@app.get("/", tags=["meta"], summary="API info")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", tags=["meta"], summary="Health check")
def health_check():
    return {"status": "ok"}

@app.get("/tasks", tags=["tasks"], summary="List tasks")
def list_tasks():
    return tasks

@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get one task")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task")
def create_task(payload: TaskCreate):
    global next_id
    new_task = {"id": next_id, "title": payload.title, "done": payload.done}
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    task["title"] = payload.title
    task["done"] = payload.done
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"], summary="Delete a task")
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return None

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]
    field = first_error["loc"][-1]
    msg = first_error["msg"]
    return JSONResponse(status_code=400, content={"error": f"Invalid {field}: {msg}"})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})