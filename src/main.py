from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.database import Base, engine, get_db
from src.models import User
from src.auth import hash_password, verify_password, create_access_token, decode_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Swiss Job Tracker API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


@app.get("/")
def root():
    return {"message": "Swiss Job Tracker API calisiyor"}


@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu email zaten kayitli")

    new_user = User(email=user.email, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email veya sifre hatali")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Gecersiz token")

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanici bulunamadi")
    return user


@app.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user