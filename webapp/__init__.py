import asyncio
import os
import threading
import traceback
from copy import copy

import aiofiles.os
import ujson
from aiohttp import web

import ultimate_alpr
from utils import is_russian_license_plate, write_frame
from webapp.constants import VIDEOS_DATA_PATH, FRAME_IMAGE_FILES_PATH, VIDEOFILES_PATH
from webapp.routes.api import api_routes
from webapp.routes.html import html_routes
from webapp.routes.static import static_routes
from webapp.video import restore, Video, Plate


def compare_strings(str1, str2):
    bigger_string = str1 if len(str1) > len(str2) else str2
    differences = 0
    for i in range(0, len(bigger_string)):
        try:
            ch1 = str1[i]
            ch2 = str2[i]
            if ch1 != ch2:
                differences += 1
        except IndexError:
            differences += 1
    return differences


def read_videos_json():
    videos = []
    for file in [file for file in os.listdir(VIDEOS_DATA_PATH) if file.endswith('.json')]:
        try:
            with open(VIDEOS_DATA_PATH + '/' + file, 'r', encoding='utf-8') as f:
                videos.append(restore(ujson.load(f)))
        except ujson.JSONDecodeError:
            pass

    return sorted(videos, key=lambda x: x.timestamp)

def read_queue():
    try:
        with open('.data/queue.json', 'r', encoding='utf-8') as f:
            return ujson.load(f)
    except FileNotFoundError:
        return []



async def on_startup(app):
    def save_queue():
        with open('.data/queue.json', 'w', encoding='utf-8') as f:
            return ujson.dump(app.queue, f)

    def get_video(filename) -> Video:
        for i, video in enumerate(app['videos']):
            if video.filename == filename:
                return video

    async def delete_video(filename):
        if not filename.lower().endswith('.mp4'):
            return False
        # Удаляем видео из памяти.
        for i, video in enumerate(app['videos']):
            if video.filename == filename:
                app['videos'].pop(i)
                break

        # Удаляем все данные, связанные с видео, с диска.
        name = filename.rsplit('.', 1)[0]
        paths = [FRAME_IMAGE_FILES_PATH, VIDEOS_DATA_PATH, VIDEOFILES_PATH]
        for path in paths:
            files = os.listdir(path)
            # Проходимся по каждому файлу в папке path1
            for file in files:
                # Проверяем, содержит ли название файла строку name
                if name in file:
                    # Создаем полный путь к файлу
                    file_path = os.path.join(path, file)
                    # Удаляем файл
                    await aiofiles.os.remove(file_path)
        return True

    def add_to_queue(filename):
        if filename in app.queue:
            return False

        app.queue.append(filename)
        return True

    def recognize_video(video: Video):
        all_plates: list[dict] = []

        def callback(plates: list[dict], frame_number, frame_image):
            """
            Callback-функция,  которая  обрабатывает  результат  распознавания  государственных  номерных  знаков.

            Аргументы:
                    plates  (list[dict]):  Список  словарей,  представляющих  распознанные  государственные  номерные  знаки.
                            Каждый  словарь  содержит  следующие  ключи:
                                    -  'text'  (str):  Текст  государственного  номерного  знака.
                                    -  'image'  (numpy.ndarray):  Изображение  государственного  номерного  знака.
                                    -  'car_image'  (numpy.ndarray):  Изображение  автомобиля  с  государственным  номерным  знаком.
                    frame_number:  Номер  текущего  кадра  в  видео.
                    frame_image  (numpy.ndarray):  Изображение  текущего  кадра.

            Возвращает:
                    bool:  True,  если  цикл  в  потоке  должен  быть  остановлен,  False  в  противном  случае.
            """
            if app.stop_recognizing:
                return True
            try:
                # Если конец. Сохраняем информацию о видео.
                if frame_number is None:
                    video.searching_frame = video.total_frames
                    video.save_sync()
                    # Удаляем видео, чтоб экономить место.
                    # os.remove(os.path.join(VIDEOFILES_PATH, video.filename))
                    app.recognizing_video = False
                    return False

                for plate in plates:
                    if is_russian_license_plate(plate['text']):
                        all_plates.append(plate)

                frame_filename = f'{frame_number}_{video.filename}.jpg'

                added_plate = False
                for i, censored_plate in enumerate(plates):
                    plate_text = censored_plate['text']
                    if is_russian_license_plate(plate_text):
                        plate_filename = f'{plate_text}_{video.filename}.jpg'
                        car_filename = f'car{i}_{frame_number}_{plate_text}_{video.filename}.jpg'
                        plate = Plate(plate_text, frame_number=frame_number, frame_filename=frame_filename,
                                      filename=plate_filename)
                        added_plate = video.add_plate(plate)
                        if added_plate:
                            write_frame(plate_filename, censored_plate['image'])
                            write_frame(car_filename, censored_plate['car_image'])
                if added_plate:
                    write_frame(frame_filename, frame_image)
                video.searching_frame = frame_number

                # Убираем ошибочные распознавания.
                video.filtered_plates.clear()
                for video_plate in video.plates:
                    main_text = video_plate.censored_text
                    # Находим похожие номера.
                    similar_strings = []
                    for plate in all_plates:
                        text = plate['text']
                        differences = compare_strings(main_text.replace('_', ''), text.replace('_', ''))
                        if differences <= 2:
                            similar_strings.append(text)
                    # Считаем сколько раз похожие номера встречаются.
                    similar_strings_amount: dict[str, int] = {}
                    for string in similar_strings:
                        try:
                            similar_strings_amount[string] += 1
                        except KeyError:
                            similar_strings_amount[string] = 1
                    # Находим номер, который встретился больше всего раз
                    biggest_amount: tuple[str, int] = ('', 0)
                    for text, amount in similar_strings_amount.items():
                        if amount > biggest_amount[1]:
                            biggest_amount = (text, amount)
                    if biggest_amount[0] == main_text:
                        video.filtered_plates.append(copy(video_plate))
                video.save_sync()
            except:
                traceback.print_exc()
            return False

        def stop_event():
            video.reset()
            app.stop_recognizing = False
            app.recognizing_video = False

        thread = threading.Thread(target=ultimate_alpr.process_video,
                                  args=(VIDEOFILES_PATH + '/' + video.filename, callback, stop_event, video.searching_frame))
        thread.start()

    async def queue_worker():
        while True:
            if not app.recognizing_video and app.queue:
                app.recognizing_video = True
                video = get_video(app.queue.pop(0))
                recognize_video(video)
                save_queue()
            await asyncio.sleep(1)

    app['videos'] = read_videos_json()
    app.queue = read_queue()
    for video in app['videos']:
        if video.searching_frame >= 0 and video.searching_frame != video.total_frames:
            app.queue.insert(0, video.filename)
            break
    app.recognizing_video = False
    app.stop_recognizing = False
    app.get_video = get_video
    app.delete_video = delete_video
    app.add_to_queue = add_to_queue
    app.save_queue = save_queue
    ultimate_alpr.init()
    asyncio.create_task(queue_worker())


async def on_cleanup(app):
    ultimate_alpr.deinit()


def run(port=80):
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.add_routes(api_routes)
    app.add_routes(html_routes)
    app.add_routes(static_routes)
    web.run_app(app, host='0.0.0.0', port=port)
