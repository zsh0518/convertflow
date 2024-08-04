import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

user_route = APIRouter(prefix="/api/user")

load_dotenv()

# 数据库配置
pg_username = os.getenv('PG_USERNAME')
pg_password = os.getenv('PG_PASSWORD')
pg_host = os.getenv('PG_HOST')
pg_database = os.getenv('PG_DATABASE')
DATABASE_URL = f"postgresql://{pg_username}:{pg_password}@{pg_host}/{pg_database}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=True, bind=engine)
Base = declarative_base()

# JWT 配置
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

# OAuth 配置
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')

# 模板配置
templates = Jinja2Templates(directory="templates")


# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    avatar_url = Column(String)
    google_id = Column(String, unique=True, index=True)
    facebook_id = Column(String, unique=True, index=True)
    twitter_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


Base.metadata.create_all(bind=engine)


# Pydantic 模型
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None


# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT 函数
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 路由
@user_route.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@user_route.get("/auth/google")
async def google_login():
    redirect_uri = "http://127.0.0.1:8088/api/user/auth/google/callback"
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&"
        f"client_id={GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope=openid%20email%20profile")


@user_route.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = "http://127.0.0.1:8088/api/user/auth/google/callback"

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not validate Google credentials")

        token_data = token_response.json()
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        if user_info_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not get user info from Google")

        user_info = user_info_response.json()

    # 用户不存在则创建新用户
    user = db.query(User).filter(User.email == user_info["email"]).first()
    if not user:
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            avatar_url=user_info.get("picture"),
            google_id=user_info["id"],
        )
        db.add(user)
    else:
        user.google_id = user_info["id"]
        user.name = user_info["name"]
        user.avatar_url = user_info.get("picture")

    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@user_route.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    # 开发验证使用
    user = db.query(User).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})
