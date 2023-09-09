import time
from typing import Optional

import aiofiles
import ujson
from jsonpickle.pickler import Pickler
from jsonpickle.unpickler import Unpickler

from webapp import VIDEOS_DATA_PATH

pickler = Pickler(numeric_keys=True)
unpickler = Unpickler()


def flatten(obj):
    return pickler.flatten(obj)


def restore(obj):
    return unpickler.restore(obj)


class Plate:
    def __init__(self, censored_text: Optional[str], text: Optional[str] = None, frame_number: Optional[int] = None,
                 frame_filename: Optional[str] = None, filename: Optional[str] = None):
        self.censored_text = censored_text
        self.text = text
        self.frame_number = frame_number
        self.frame_filename = frame_filename
        self.filename = filename


class Video:
    def __init__(self, filename: str, total_frames: Optional[int] = None, fps: Optional[int] = None):
        self.filename = filename
        self.total_frames = total_frames
        self.fps = fps
        self.timestamp = time.time()
        self.plates: list[Plate] = []
        self.filtered_plates: list[Plate] = []
        self.searching_frame = -1
        self.recognizing_frame = -1


    def add_plate(self, plate: Plate):
        for p in self.plates:
            if p.censored_text == plate.censored_text:
                return False
        self.plates.append(plate)
        return True

    async def save(self):
        filepath = VIDEOS_DATA_PATH + '/' + self.filename.split('.')[0] + '.json'
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(ujson.dumps(flatten(self)))

    def save_sync(self):
        filepath = VIDEOS_DATA_PATH + '/' + self.filename.split('.')[0] + '.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ujson.dumps(flatten(self)))

    def tojson(self):
        return flatten(self)

    def reset(self):
        self.plates = []
        self.filtered_plates = []
        self.searching_frame = -1
        self.recognizing_frame = -1
        self.save_sync()
