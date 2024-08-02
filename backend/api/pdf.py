import os
import shutil
import tempfile
import zipfile
from typing import List

from fastapi import File, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter
from starlette.background import BackgroundTask

pdf_route = APIRouter(prefix="/api/pdf")


def is_pdf(file: UploadFile) -> bool:
    return file.filename.lower().endswith('.pdf')


def split_pdf(input_path: str, output_folder: str, pages_per_file: int) -> List[str]:
    output_files = []
    with open(input_path, 'rb') as file:
        pdf = PdfReader(file)
        total_pages = len(pdf.pages)

        for start in range(0, total_pages, pages_per_file):
            pdf_writer = PdfWriter()
            end = min(start + pages_per_file, total_pages)

            for page in range(start, end):
                pdf_writer.add_page(pdf.pages[page])

            output_filename = f'split_{start + 1}-{end}.pdf'
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            output_files.append(output_path)

    return output_files


def create_zip(files: List[str], zip_path: str):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))


@pdf_route.post("/split")
async def split_pdf_api(file: UploadFile = File(...), pages: int = Form(...)):
    if not is_pdf(file):
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")

    if pages <= 0:
        raise HTTPException(status_code=400, detail="Pages must be a positive integer")

    temp_dir = tempfile.mkdtemp()
    try:
        temp_input_path = os.path.join(temp_dir, "input.pdf")
        with open(temp_input_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        output_folder = os.path.join(temp_dir, "output")
        os.makedirs(output_folder)

        split_files = split_pdf(temp_input_path, output_folder, pages)

        zip_filename = "split_pdfs.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        create_zip(split_files, zip_path)

        return FileResponse(
            zip_path,
            filename=zip_filename,
            media_type='application/zip',
            background=BackgroundTask(cleanup_temp_dir, temp_dir)
        )

    except Exception as e:
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@pdf_route.get("/api/pdf/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("temp", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")


def merge_pdfs(input_files: List[str], output_path: str):
    pdf_writer = PdfWriter()

    for file_path in input_files:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)


@pdf_route.post("/merge")
async def merge_pdf_api(files: List[UploadFile] = File(...)):
    if not all(is_pdf(file) for file in files):
        raise HTTPException(status_code=400, detail="All uploaded files must be PDFs")

    # 创建一个持久的临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        temp_input_files = []
        for file in files:
            temp_input_path = os.path.join(temp_dir, file.filename)
            with open(temp_input_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
            temp_input_files.append(temp_input_path)

        output_filename = "merged.pdf"
        output_path = os.path.join(temp_dir, output_filename)

        merge_pdfs(temp_input_files, output_path)

        # 确保文件存在
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to create merged PDF")

        # 使用 background 参数来确保文件在响应发送后被删除

        return FileResponse(output_path, filename=output_filename,
                            background=BackgroundTask(cleanup_temp_dir, temp_dir))
    except Exception as e:
        # 如果发生任何错误，确保删除临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def cleanup_temp_dir(temp_dir: str):
    shutil.rmtree(temp_dir, ignore_errors=True)


@pdf_route.post("/encrypt")
async def encrypt_pdf_api(file: UploadFile = File(...), password: str = Form(...)):
    if not is_pdf(file):
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")

    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    # 创建一个临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 保存上传的文件
        temp_input_path = os.path.join(temp_dir, "input.pdf")
        with open(temp_input_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # 创建输出文件路径
        output_filename = "encrypted.pdf"
        output_path = os.path.join(temp_dir, output_filename)

        # 加密PDF
        encrypt_pdf(temp_input_path, output_path, password)

        # 确保文件存在
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to create encrypted PDF")

        # 返回加密后的文件，并在响应发送后清理临时目录
        return FileResponse(output_path, filename=output_filename,
                            background=BackgroundTask(cleanup_temp_dir, temp_dir))

    except Exception as e:
        # 如果发生任何错误，确保删除临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def encrypt_pdf(input_path: str, output_path: str, password: str):
    pdf_writer = PdfWriter()
    pdf_reader = PdfReader(input_path)

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    pdf_writer.encrypt(password)

    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)
