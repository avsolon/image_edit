from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload")
async def upload(
    file: UploadFile,
    format: str = Form(...),
    width: int = Form(None),
    height: int = Form(None),
    keepRatio: str = Form("true")
):
    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "Файл слишком большой")

    try:
        img = Image.open(io.BytesIO(contents))
    except:
        raise HTTPException(400, "Невалидное изображение")

    if format not in ["jpeg", "png", "webp"]:
        raise HTTPException(400, "Неверный формат")

    img = img.convert("RGB")

    # resize
    if width or height:
        if keepRatio == "true":
            img.thumbnail((width or img.width, height or img.height))
        else:
            img = img.resize((width or img.width, height or img.height))

    buf = io.BytesIO()
    img.save(buf, format.upper())
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/" + format)