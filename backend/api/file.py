from fastapi import UploadFile, APIRouter
from fastapi.responses import HTMLResponse

file_route = APIRouter(prefix="/api/file")


@file_route.post("/uploadFiles")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@file_route.post("/uploadFile/")
async def create_upload_files(file: UploadFile | None = None):
    if not file:
        return {"message not found"}
    else:
        return {"filename": file.filename}


@file_route.get("/")
async def main():
    content = """
<body>
<form action="/api/file/uploadFiles" enctype="multipart/form-data" method="post">
<input name="files" type="file">
<input type="submit">
</form>
<form action="/api/file/uploadFile/" enctype="multipart/form-data" method="post">
<input name="files" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
