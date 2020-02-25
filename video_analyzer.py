#!/usr/local/bin/python
import re
import sys

import ffmpeg
import numpy as np
import PIL
import youtube_dl

from image_classifier import predict


def find_events_by_class(path, classes, start=0):
    process1 = (
        ffmpeg
        .input(path, ss=start)
        .filter('fps', 1)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run_async(pipe_stdout=True, quiet=True)
    )
    i = start
    result = []
    stream = ffmpeg.probe(path)['streams'][0]
    width = int(stream['width'])
    height = int(stream['height'])
    while True:
        in_bytes = process1.stdout.read(width * height * 3)
        if not in_bytes:
            break

        img = PIL.Image.fromarray(np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3]))
        img = img.resize((224, 224), PIL.Image.NEAREST)
        cls, _ = predict(img)
        if cls in classes:
            result.append((i, cls))
        i += 1
    return result


def download_progress_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': 'videos/%(id)s',
        'noplaylist': True,
        'writeinfojson': True,
        'progress_hooks': [download_progress_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename


if __name__ == '__main__':
    video_path = sys.argv[1]
    if re.match('https?://', video_path):
        video_file_path = download_video(video_path)
    else:
        video_file_path = video_path

    events = find_events_by_class(video_file_path, classes=(
        'game', 'goal', 'results',
    ))
    print(events)
