import cv2
import os
import shutil

from app.script import *


def transfer(src, dst, tp):
    print("INFO: Starting process video")
    print(src + " to : " + dst)
    print("temp file:" + tp)

    frames = cv2.VideoCapture(src)
    foucc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(dst, foucc, 15, (1000, 720))
    i = 0
    while frames.isOpened():
        frame = frames.read()[1]
        if frame is None:
            break
        frame = frame[0:720, 0:1000]
        cv2.imwrite(tp + "/{:0>3}.jpg".format(i), frame)
        i = i + 1

    files = os.listdir(tp)
    for file in files:
        img = cv2.imread(os.path.join(tp, file))
        video.write(img)

    frames.release()
    video.release()

    v_files = os.listdir(tp)
    for v_file in v_files:
        os.remove(os.path.join(tp, v_file))

    print("INFO: video process finished!")


if __name__ == '__main__':
    transfer(r'F:\flask_project\app\static\video\up_paper\孙江山111-msr-2021-04-14T03-31-17-212Z.mp4',
             r'F:\flask_project\app\static\video\up_paper\2.mp4',
             'F:/flask_project/app/static/video/up_paper/temp/')
