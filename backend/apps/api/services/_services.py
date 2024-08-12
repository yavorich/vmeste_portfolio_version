import os
import random
from moviepy.editor import VideoFileClip

from apps.api.models import EventMedia
from config.settings import MEDIA_ROOT


def generate_confirmation_code():
    return "".join([str(random.randint(0, 9)) for _ in range(5)])


def generate_video_preview(instance: EventMedia):
    clip = VideoFileClip(instance.file.path)
    preview_dir = os.path.join(MEDIA_ROOT, "previews")
    if not os.path.exists(preview_dir):
        os.mkdir(preview_dir)
    preview_filename = instance.file.name.split("/")[-1] + "_preview.png"
    preview_path = os.path.join(preview_dir, preview_filename)
    clip.save_frame(
        preview_path, t=clip.duration / 2
    )  # Генерация превью из середины видео
    return os.path.join("previews", preview_filename)
