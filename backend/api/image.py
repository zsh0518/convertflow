import io
import os
import shutil
import tempfile
import zipfile
from enum import Enum
from typing import List

import replicate
from PIL import ImageDraw, ImageFont, Image
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from pydantic import BaseModel, Field
from rembg import remove
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, StreamingResponse

image_route = APIRouter(prefix="/api/image")

load_dotenv()


class JoinDirection(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


def cleanup_temp_dir(temp_dir: str):
    shutil.rmtree(temp_dir, ignore_errors=True)


@image_route.post("/add-watermark")
async def add_watermark_to_images(
        files: List[UploadFile] = File(...),
        watermark_text: str = Form(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No image files provided")

    # 如果只有一个文件，直接处理并返回
    if len(files) == 1:
        image = Image.open(files[0].file)
        watermarked_image = add_watermark(image, watermark_text)

        img_byte_arr = io.BytesIO()
        watermarked_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(img_byte_arr, media_type="image/png",
                                 headers={"Content-Disposition": f"attachment; filename=watermarked_image.png"})

    # 如果有多个文件，处理所有文件并创建ZIP
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "watermarked_images.zip")

            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for file in files:
                    image = Image.open(file.file)
                    watermarked_image = add_watermark(image, watermark_text)

                    img_byte_arr = io.BytesIO()
                    watermarked_image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)

                    zip_file.writestr(f"{file.filename}_watermarked.png", img_byte_arr.getvalue())

            return FileResponse(
                zip_path,
                media_type="application/zip",
                filename="watermarked_images.zip"
            )


def add_watermark(image: Image.Image, watermark_text: str) -> Image.Image:
    # 创建一个绘图对象
    draw = ImageDraw.Draw(image)

    # 设置字体
    try:
        font = ImageFont.truetype("arial", 360)
    except IOError:
        font = ImageFont.load_default()

    # 获取图像尺寸
    width, height = image.size

    # 获取文本边界框
    left, top, right, bottom = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = right - left
    text_height = bottom - top

    # 计算文本位置（右下角）
    x = width - text_width - 10
    y = height - text_height - 10

    # 添加水印文本
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))

    return image


@image_route.post("/remove-background")
async def remove_image_background(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided")

    temp_dir = tempfile.mkdtemp()
    try:
        # 保存上传的文件到临时目录
        temp_input_path = os.path.join(temp_dir, file.filename)
        with open(temp_input_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # 读取图片并移除背景
        input_image = Image.open(temp_input_path)
        output_image = remove(input_image)

        # 保存处理后的图片
        output_filename = f"removed_bg_{file.filename}"
        output_path = os.path.join(temp_dir, output_filename)
        output_image.save(output_path, format="PNG")

        # 确保文件存在
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to create image with removed background")

        # 使用 BackgroundTask 来确保在响应发送后删除临时目录
        return FileResponse(
            output_path,
            filename=output_filename,
            media_type="image/png",
            background=BackgroundTask(cleanup_temp_dir, temp_dir)
        )

    except Exception as e:
        # 如果发生任何错误，确保删除临时目录
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@image_route.post("/join")
async def join_images(
        files: List[UploadFile] = File(...),
        direction: JoinDirection = Form(JoinDirection.VERTICAL)
):
    if not files:
        raise HTTPException(status_code=400, detail="No image files provided")

    temp_dir = tempfile.mkdtemp()
    try:
        images = []
        for file in files:
            temp_input_path = os.path.join(temp_dir, file.filename)
            with open(temp_input_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
            img = Image.open(temp_input_path)
            images.append(img)

        # 垂直拼接，选取宽度最大的图片的宽度作为拼接后的图片宽度
        if direction == JoinDirection.VERTICAL:
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            joined_image = Image.new('RGB', (max_width, total_height))
            y_offset = 0
            for img in images:
                if img.width < max_width:
                    new_img = Image.new('RGB', (max_width, img.height), (255, 255, 255))
                    new_img.paste(img, ((max_width - img.width) // 2, 0))
                    img = new_img
                joined_image.paste(img, (0, y_offset))
                y_offset += img.height
        # 水平拼接，选取高度最大的图片的高度作为拼接后的图片高度
        else:  # HORIZONTAL
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            joined_image = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for img in images:
                if img.height < max_height:
                    new_img = Image.new('RGB', (img.width, max_height), (255, 255, 255))
                    new_img.paste(img, (0, (max_height - img.height) // 2))
                    img = new_img
                joined_image.paste(img, (x_offset, 0))
                x_offset += img.width

        output_filename = f"joined_image.png"
        output_path = os.path.join(temp_dir, output_filename)
        joined_image.save(output_path, format="PNG")

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to create joined image")

        return FileResponse(
            output_path,
            filename=output_filename,
            media_type="image/png",
            background=BackgroundTask(cleanup_temp_dir, temp_dir)
        )

    except Exception as e:
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@image_route.post("/upscale")
async def upscale(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # 将上传的文件内容写入临时文件
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        output = replicate.run(
            "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
            input={
                "image": open(temp_file_path, "rb"),
                "scale": 2,
                "face_enhance": True
            }
        )
        print(output)
        return {"result": output}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # 删除临时文件
        os.unlink(temp_file_path)


class AspectRatio(str, Enum):
    SQUARE = "1:1"
    WIDESCREEN = "16:9"
    ULTRAWIDE = "21:9"
    PORTRAIT = "2:3"
    LANDSCAPE = "3:2"
    FOUR_FIVE = "4:5"
    FIVE_FOUR = "5:4"
    WIDESCREEN_REVERSED = "9:16"
    ULTRAWIDE_REVERSED = "9:21"


class OutputFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="用户输入的提示词")
    aspect_ratio: AspectRatio = Field(default=AspectRatio.SQUARE, description="图像比例")
    num_outputs: int = Field(default=1, ge=1, le=4, description="生成图像数量")
    output_format: OutputFormat = Field(default=OutputFormat.WEBP, description="生成图像格式")
    output_quality: int = Field(default=90, ge=1, le=100, description="生成图像质量")
    disable_safety_checker: bool = Field(default=False, description="安全性检查")


class ImageGenerationResponse(BaseModel):
    images: list[str] = Field(..., description="生成的地址列表")


@image_route.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest = Body(...)):
    # 这里实现图像生成的逻辑
    # 使用request中的参数调用相应的API或服务
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": request.prompt,
            "num_outputs": request.num_outputs,
            "aspect_ratio": request.aspect_ratio,
            "output_format": request.output_format,
            "output_quality": request.output_quality,
            "disable_safety_checker": request.disable_safety_checker
        }
    )
    # 示例返回值（实际实现时需要替换）
    print(output)
    return ImageGenerationResponse(images=output)
