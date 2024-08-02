import os
import shutil
import tempfile
from typing import List

from fastapi import File, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter

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


@pdf_route.post("/split")
async def split_pdf_api(file: UploadFile = File(...), pages: int = Form(...)):
    print(f"pages: {pages}")
    if not is_pdf(file):
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")

    if pages <= 0:
        raise HTTPException(status_code=400, detail="Pages must be a positive integer")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_input_path = os.path.join(temp_dir, "input.pdf")
        print(f"temp_input_path: {temp_input_path}")
        with open(temp_input_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        output_folder = os.path.join(temp_dir, "output")
        os.makedirs(output_folder)

        split_files = split_pdf(temp_input_path, output_folder, pages)

        return {"split_files": [os.path.basename(f) for f in split_files]}


@pdf_route.get("/api/pdf/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("temp", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
