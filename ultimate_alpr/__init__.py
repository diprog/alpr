import json
import os
import signal
import traceback


import cv2
import numpy as np
import psutil
import ultimateAlprSdk
from PIL import Image, ExifTags, ImageOps

from ultimate_alpr.config import JSON_CONFIG

IMAGE_TYPES_MAPPING = {
    'RGB': ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_RGB24,
    'RGBA': ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_RGBA32,
    'L': ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_Y
}


def load_pil_image(pil_image):
    img_exif = pil_image.getexif()
    ret = {}
    orientation = 1
    try:
        if img_exif:
            for tag, value in img_exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                ret[decoded] = value
            orientation = ret["Orientation"]
    except Exception as e:
        print("An exception occurred: {}".format(e))
        traceback.print_exc()

    if orientation > 1:
        pil_image = ImageOps.exif_transpose(pil_image)

    if pil_image.mode in IMAGE_TYPES_MAPPING:
        image_type = IMAGE_TYPES_MAPPING[pil_image.mode]
    else:
        raise ValueError(f"Invalid mode: {pil_image.mode}")

    return pil_image, image_type


def init():
    ultimateAlprSdk.UltAlprSdkEngine_init(json.dumps(JSON_CONFIG))


def deinit():
    ultimateAlprSdk.UltAlprSdkEngine_deInit()


def process_image(img):
    # Параметр image должен быть из cv2
    # Преобразование кадра в изображение Pillow
    image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    image, image_type = load_pil_image(image)
    width, height = image.size

    # Process an image
    result = ultimateAlprSdk.UltAlprSdkEngine_process(
        image_type,
        image.tobytes(),  # type(x) == bytes
        width,
        height,
        0,  # stride
        1  # exifOrientation (already rotated in load_image -> use default value: 1)
    )
    if result.isOK():
        print(result.json())
        return json.loads(result.json())
    else:
        try:
            current_system_pid = os.getpid()
            ThisSystem = psutil.Process(current_system_pid)
            ThisSystem.terminate()
        except:
            os.kill(os.getpid(), signal.SIGINT)


def image_from_warpedbox(image, warped_box):
    # Создание массива точек warped_box
    points = np.array(warped_box, dtype=np.float32).reshape((-1, 1, 2))

    # Размеры прямоугольной области для обрезки
    width = max(warped_box[0], warped_box[2], warped_box[4], warped_box[6]) - min(warped_box[0], warped_box[2],
                                                                                  warped_box[4], warped_box[6])
    height = max(warped_box[1], warped_box[3], warped_box[5], warped_box[7]) - min(warped_box[1], warped_box[3],
                                                                                   warped_box[5], warped_box[7])

    # Создание матрицы преобразования перспективы
    matrix = cv2.getPerspectiveTransform(points,
                                         np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32))

    # Применение преобразования перспективы
    warped_image = cv2.warpPerspective(image, matrix, (int(width), int(height)))

    # Отображение результата
    return warped_image


def process_video(filepath, callback, stop_event, start_frame):
    video = cv2.VideoCapture(filepath)

    if start_frame >= 0:
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frames_per_second = video.get(cv2.CAP_PROP_FPS)
    frame_skip = int(frames_per_second / 4) - 1

    stopped = False
    while True:
        for _ in range(frame_skip):
            video.read()
        ret, frame = video.read()
        if not ret:
            callback(None, None, None)
            break

        result = process_image(frame)
        try:
            if plates := result.get('plates'):
                plates = [p for p in plates if p.get('text')]
                for plate in plates:
                    plate['image'] = image_from_warpedbox(frame, plate['warpedBox'])
                    plate['car_image'] = image_from_warpedbox(frame, plate['car']['warpedBox'])
                    plate['text'] = plate['text'].replace('*', '_')
            else:
                plates = []
            stop = callback(plates, int(video.get(cv2.CAP_PROP_POS_FRAMES)), frame)
            if stop:
                stopped = True
                break
        except:
            traceback.print_exc()

    video.release()

    if stopped:
        stop_event()
