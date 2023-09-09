import os

import cv2
import ujson

VIDEOS_DATA_PATH = '.data/videos_json'
VIDEOFILES_PATH = '.data/videos'
def read_videos_json():
    videos = []
    for file in [file for file in os.listdir(VIDEOS_DATA_PATH) if file.endswith('.json')]:
        try:
            with open(VIDEOS_DATA_PATH + '/' + file, 'r', encoding='utf-8') as f:
                videos.append(ujson.load(f))
        except ujson.JSONDecodeError:
            pass

    return videos

videos = read_videos_json()
print(videos)
for video in videos:
    filepath = VIDEOFILES_PATH + '/' + video['filename']
    cv2_video = cv2.VideoCapture(filepath)
    fps = float(cv2_video.get(cv2.CAP_PROP_FPS))
    video['fps'] = fps
    with open(VIDEOS_DATA_PATH + '/' + video['filename'].split('.')[0] + '.json', 'w', encoding='utf-8') as f:
        ujson.dump(video, f)

print()