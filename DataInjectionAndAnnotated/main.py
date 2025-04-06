from fastapi import FastAPI, Depends, Header, Path, HTTPException, status
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()

async def get_db_session():
    print("DB session > start")
    session = {"data": {1: {"name": "Item one"}, 2: {"name": "Item two"}}}
    try:
        yield session
    finally:
        print("DB session < teardown")

DBsession = Annotated[dict, Depends(get_db_session)]

async def get_user(token: Annotated[str| None, Header()]=None):
    print("Checking auth..")
    user = {"username": "test_user"}
    return user

CurrentUser = Annotated[dict, Depends(get_user)]

class ItemCreate(BaseModel):
    name: str
    price: float | None = None

@app.post("/item")
async def create_item(
    item: ItemCreate,
    db: DBsession,
    user: CurrentUser):
    print(f"User {user['username']} creating item")
    new_id = max(db["data"].keys() or [0]) + 1
    db["data"][new_id] = item.model_dump()
    return {"id": new_id, **item.model_dump()}

@app.get("/item/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(ge=1)],
    db: DBsession
    ):
    print("reading Items")
    if item_id not in db["data"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Item is not present")
    return {"id": item_id, **db["data"][item_id]}
