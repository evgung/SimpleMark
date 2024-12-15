# -*- coding: utf-8 -*-
import os
import cv2
import time

class VideoFrameExtractor:
    def __init__(self, video_file, output_dir="frames2", fps=10, save_width=True, frame_width=800):
        self.video_file = video_file
        self.output_dir = os.path.join(output_dir, 'frames')
        self.frame_width = frame_width  # если указано изменение ширины
        self.frame_counter = 0
        self.camera = None

        self.cooldown = 1 / fps  # период сохранения кадров (в секундах)
        self.save_width = save_width  # использовать исходную ширину? (bool)
        self.fp = ""
        self.fn = ""

    def create_output_directory(self):
        # здесь создаются папки, которые есть по пути
        # напоминаю, что на пути сохранения не должно быть кириллицы
        os.makedirs(self.output_dir, exist_ok=True)

    def open_video(self):
        self.camera = cv2.VideoCapture(self.video_file)
        if not self.camera.isOpened():
            raise ValueError(f"Видео открыть не удалось»: {self.video_file}")

    def getVideoName(self, path):
        return os.path.basename(path)

    def getInfo(self):
        vid_name = self.getVideoName(self.video_file).split('.')[0]
        self.fp = os.path.join(self.output_dir, vid_name + '_')
        self.fn = vid_name + '_'
        return self.fp, self.fn

    def extract_frames(self):
        self.create_output_directory()
        self.open_video()

        vid_name = self.getVideoName(self.video_file).split('.')[0]
        last_time = 0
        while True:
            ok_flag, frame = self.camera.read()
            if time.time() - last_time >= self.cooldown and ok_flag:
                file_name = ""
                if not self.save_width:
                    d_width = self.frame_width / frame.shape[1]
                    frame_resized = cv2.resize(frame, None, fx=d_width, fy=d_width)
                    file_name = os.path.join(self.output_dir, f"{vid_name}_{str(self.frame_counter)}.png")
                    cv2.imwrite(file_name, frame_resized)
                else:
                    file_name = os.path.join(self.output_dir, f"{vid_name}_{str(self.frame_counter)}.png")
                    cv2.imwrite(file_name, frame)
                if not self.save_width:
                    cv2.imshow('Video', frame_resized)
                else:
                    cv2.imshow('Video', frame)
                self.frame_counter += 1
                last_time = time.time()
            elif not ok_flag:
                break
            if cv2.waitKey(1) == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
