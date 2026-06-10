from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os

from main import screen_resume

app = FastAPI(
    title="Resume Screener API"
)

UPLOAD_DIR = "../data/uploads"


@app.get("/")
def home():
    return {
        "message": "Resume Screener API Running"
    }


@app.post("/screen")
async def screen(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_DIR,
        resume.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            resume.file,
            buffer
        )

    result = screen_resume(
        file_path,
        job_description
    )

    return result