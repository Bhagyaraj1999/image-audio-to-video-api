from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
import os
import subprocess
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploaded videos
app.mount("/videos", StaticFiles(directory=UPLOAD_DIR), name="videos")

@app.post("/generate-video/")
async def generate_video(image: UploadFile = File(...), audio: UploadFile = File(...)):
    # Generate unique filenames
    unique_id = str(uuid.uuid4())
    image_path = f"{UPLOAD_DIR}/{unique_id}_image.jpg"
    audio_path = f"{UPLOAD_DIR}/{unique_id}_audio.mp3"
    output_path = f"{UPLOAD_DIR}/{unique_id}_output.mp4"

    # Save uploaded files
    with open(image_path, "wb") as img_file:
        img_file.write(await image.read())
    with open(audio_path, "wb") as aud_file:
        aud_file.write(await audio.read())

    # Run FFmpeg command
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:a", "aac",
        "-c:v", "libx264",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-t", "120",
        "-shortest",
        "-y",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail="Video generation failed")

    video_url = f"/videos/{unique_id}_output.mp4"
    return {"video_url": video_url}

@app.get("/")
def home():
    return {
        "message": "Image + Audio to Video API",
        "instructions": "POST /generate-video/ with image and audio files"
    }