import math
from copy import copy

import cv2

from webapp.constants import FRAME_IMAGE_FILES_PATH


def is_russian_license_plate(plate: str) -> bool:
    if len(plate) < 8 or len(plate) > 9:
        return False
    plate = copy(plate).replace('_', '0')
    region = plate[:1]
    if not region.isalpha() or not region.isupper():
        return False
    if not plate[1:4].isdigit():
        return False
    if not plate[4:6].isalpha() or not plate[4:6].isupper():
        return False
    if not plate[6:].isdigit():
        return False
    return True

from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwds):
    # Code to acquire resource, e.g.:
    resource = acquire_resource(*args, **kwds)
    try:
        yield resource
    finally:
        # Code to release resource, e.g.:
        release_resource(resource)


def write_frame(filename, cv2_image):
    cv2.imwrite(f'{FRAME_IMAGE_FILES_PATH}/{filename}', cv2_image)

def get_video_duration(cv2_video):
    fps = cv2_video.get(cv2.CAP_PROP_FPS)
    total_frames = int(cv2_video.get(cv2.CAP_PROP_FRAME_COUNT))

    duration_seconds = total_frames / fps
    duration = str(math.floor(duration_seconds / 3600)).zfill(2) + ":" + \
               str(math.floor((duration_seconds % 3600) / 60)).zfill(2) + ":" + \
               str(math.floor(duration_seconds % 60)).zfill(2)
    return duration