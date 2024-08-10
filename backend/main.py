import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from api.file import file_route
from api.image import image_route
from api.pdf import pdf_route
from api.user import user_route

app = FastAPI()
app.include_router(file_route)
app.include_router(pdf_route)
app.include_router(image_route)
app.include_router(user_route)

# 添加 SessionMiddleware,
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

if __name__ == '__main__':
    load_dotenv()
    uvicorn.run(app, host="0.0.0.0", port=8088)
