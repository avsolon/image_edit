from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
import io

app = FastAPI(root_path="/api")

MAX_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    format: str = Form("jpeg"),
    width: int = Form(None),
    height: int = Form(None),
    keepRatio: bool = Form(True),
):
    contents = await file.read()

    # 🔒 size limit
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой (max 5MB)")

    # 🖼 image open
    try:
        img = Image.open(io.BytesIO(contents))
        img.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Невалидное изображение")

    # 🎯 format validation
    format = format.lower()
    if format not in ["jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Неверный формат")

    # 🧠 convert mode (важно для jpeg)
    if format == "jpeg":
        img = img.convert("RGB")

    # 📏 resize logic
    if width or height:
        w = width or img.width
        h = height or img.height

        if keepRatio:
            img.thumbnail((w, h))
        else:
            img = img.resize((w, h))

    # 💾 output buffer
    buf = io.BytesIO()

    save_format = "JPEG" if format == "jpeg" else format.upper()

    img.save(buf, format=save_format)
    buf.seek(0)

    # 📤 response
    return StreamingResponse(
        buf,
        media_type=f"image/{format}",
        headers={
            "Content-Disposition": f"attachment; filename=converted.{format}"
        }
    )