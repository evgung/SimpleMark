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

        self.fps = fps      # желаемый fps
        self.video_fps = 0  # реальный fps видео
        self.save_width = save_width  # использовать исходную ширину? (bool)
        self.fp = ""
        self.fn = ""

    def create_output_directory(self):
        # здесь создаются папки, которые есть по пути
        # напоминаю, что на пути сохранения не должно быть кириллицы
        os.makedirs(self.output_dir, exist_ok=True)

    def open_video(self):
        self.camera = cv2.VideoCapture(self.video_file)
        self.video_fps = self.camera.get(cv2.CAP_PROP_FPS)
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

        # Рассчитываем интервал между сохранением кадров
        save_interval = int(self.video_fps / self.fps)  # Интервал в кадрах

        vid_name = self.getVideoName(self.video_file).split('.')[0]
        frame_counter = 0
        save_counter = 0

        while True:
            ok_flag, frame = self.camera.read()
            if not ok_flag:
                break

            # Сохраняем кадр, если он попадает в интервал
            if frame_counter % save_interval == 0:
                if not self.save_width:
                    d_width = self.frame_width / frame.shape[1]
                    frame = cv2.resize(frame, None, fx=d_width, fy=d_width)

                file_name = os.path.join(self.output_dir, f"{vid_name}_{str(save_counter)}.png")
                is_success, im_buf_arr = cv2.imencode(".png", frame)
                im_buf_arr.tofile(file_name)
                cv2.imshow('Video', frame)

                save_counter += 1

            frame_counter += 1

            if cv2.waitKey(1) == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
