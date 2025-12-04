from fastapi import FastAPI
import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Secure Authentication System")


# -------------------------
# SQlite Db
# -------------------------

DB_URL = "sqlite:///db.sqlite"
engine = create_engine(DB_URL, echo=True)

# -------------------------
# User model
# -------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    password_hash: str
    totp_secret: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password_hash: str


# -------------------------
# DB Initializing 
# -------------------------

def init_db():
    SQLModel.metadata.create_all(engine)

init_db()

# -------------------------
# endpoints
# -------------------------

# main endpoint
@app.get("/")
def root():
    return {"message": "FastAPI server running!"}


# showing user info
@app.post("/users/")
def create_user(user: UserCreate):
    db_user = User(username=user.username, email=user.email, password_hash=user.password_hash)
    with Session(engine) as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}


@app.get("/users/", response_model=List[User])
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users


# @app.get("/auth/test")
# def test_auth():
#     return {"status": "auth endpoint works"}



