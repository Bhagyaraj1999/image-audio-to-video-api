from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid
import os
import subprocess

app = FastAPI()

# Create uploads folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Serve the uploads folder statically
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.post("/make-video/")
async def make_video(image: UploadFile = File(...), audio: UploadFile = File(...)):
    # Generate unique filenames
    img_path = f"uploads/{uuid.uuid4()}_{image.filename}"
    audio_path = f"uploads/{uuid.uuid4()}_{audio.filename}"
    output_path = f"uploads/{uuid.uuid4()}_output.mp4"

    # Save uploaded image
    with open(img_path, "wb") as f:
        f.write(await image.read())

    # Save uploaded audio
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Run ffmpeg to create video
    command = [
        "ffmpeg",
        "-y",  # Overwrite if exists
        "-loop", "1",
        "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    video_url = f"/uploads/{os.path.basename(output_path)}"
    return JSONResponse(content={"video_url": video_url})
