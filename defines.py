import requests
from PIL import Image
from io import BytesIO
import random


def get_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    save_path = f"{random.randint(10000000000, 1000000000000)}.png"
    with open(save_path, "wb") as f:
        f.write(response.content)
    return save_path


def human_duration(minute_duration):
    hours = minute_duration // 60
    minutes = minute_duration % 60
    if hours == 0:
        return f"{minutes} мин."
    if minutes == 0:
        return f"{hours} ч."
    return f"{hours} ч. {minutes} мин."