import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image

app = FastAPI()

# CORS (для фронта / другого домена)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # потом можно ограничить доменом
    allow_methods=["*"],
    allow_headers=["*"],
)

# Лимиты
MAX_SIZE = 5 * 1024 * 1024  # 5MB
MAX_WIDTH = 5000
MAX_HEIGHT = 5000

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    format: str = Form(...),
    width: int = Form(None),
    height: int = Form(None),
    keepRatio: str = Form("true"),
):

    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой (max 5MB)")

    try:
        img = Image.open(io.BytesIO(contents))
    except:
        raise HTTPException(status_code=400, detail="Невалидное изображение")

    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
        raise HTTPException(status_code=400, detail="Слишком большое изображение (max 5000px)")

    if format not in ["jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат")

    img = img.convert("RGB")

    if width or height:
        width = width or img.width
        height = height or img.height

        if keepRatio == "true":
            img.thumbnail((width, height))
        else:
            img = img.resize((width, height))

    buf = io.BytesIO()
    img.save(buf, format.upper())
    buf.seek(0)

    original_name = file.filename.rsplit(".", 1)[0]
    filename = f"{original_name}.{format}"

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        buf,
        media_type=f"image/{format}",
        headers=headers
    )