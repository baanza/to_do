from fastapi import FastAPI, Depends, Query, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Annotated
from sqlmodel import SQLModel, Session, create_engine, select,  Field
import uuid


class to_do(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    time_created : datetime
    description: str
    done: str = Literal["done", "not done"]

class userto_do(BaseModel):
    title: str
    description: str
    done: str = Literal["done", "not done"]


engine = create_engine("sqlite:///main.db")

def sessionyielder():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

sesh = Annotated[Session, Depends(sessionyielder)]

app = FastAPI()

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)


@app.post("/todos/")
async def add_items(item: userto_do, session: sesh):
    item_to_be_added = to_do(
        id = str(uuid.uuid4()),
        title= item.title,
        time_created = datetime.now(),
        description = item.description,
        done = item.done
    )
    session.add(item_to_be_added)
    session.commit()
    return {
        "somesing": "happened anyways"
    }

@app.get("/todos/")
async def return_items(session: sesh):
    elements = session.exec(select(to_do)).all()
    return elements

class queries(BaseModel):
    title: None | str
    done: None | str = Literal["done", "not done"]

@app.get("/queried_todos/")
async def query_todos(q: Annotated[queries, Query], session: sesh):
    if q.title and q.done:
        statement = select(to_do).where(to_do.title == q.title, to_do.done == to_do.done)
        items = session.exec(statement).all()
    else:
        if q.title:
            items = session.exec(select(to_do).where(to_do.title == q.title)).all()
        elif q.done:
            items = session.exec(select(to_do).where(to_do.done == q.done))
        else:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="The queries are not queried")
    
    return items


