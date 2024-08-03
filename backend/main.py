import uvicorn
from fastapi import FastAPI

from api.file import file_route
from api.pdf import pdf_route
from api.image import image_route

app = FastAPI()
app.include_router(file_route)
app.include_router(pdf_route)
app.include_router(image_route)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8088)
