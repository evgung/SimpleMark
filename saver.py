import os
import pickle
import cv2
import numpy as np


class Saver:

    def __init__(self, project_path):
        self.project_path = project_path
        self.config_file = os.path.join(project_path, "config.pkl")
        self.info_path = os.path.join(project_path, "info")
        self.dataset_path = os.path.join(project_path, "dataset")
        os.makedirs(self.info_path, exist_ok=True)
        os.makedirs(self.dataset_path, exist_ok=True)

    def saveProject(self, last_frame_number, path_to_video, last_extracted_frame_number, fps, image_name, image_path):
        properties = {
            "last_frame_number": last_frame_number,
            "path_to_video": path_to_video,
            "last_extracted_frame_number": last_extracted_frame_number,
            "fps": fps,
            "image_name": image_name,
            "image_path": image_path
        }

        with open(self.config_file, 'wb') as config:
            pickle.dump(properties, config)

    # points - массив объектов класса Point
    def saveFramePoints(self, frame_number, points):
        info_file = os.path.join(self.info_path, str(frame_number))

        if len(points) == 0:
            if os.path.exists(info_file):
                os.remove(info_file)
        else:
            with open(info_file, 'wb') as frame_file:
                pickle.dump(points, frame_file)

    def saveDataset(self, frames_mask_with_path):
        i = 0
        for path_name, dirs, file_names in os.walk(self.info_path):
            for frame_number in file_names:

                with open(os.path.join(path_name, frame_number), 'rb') as info_file:
                    points = pickle.load(info_file)
                    frame_path = frames_mask_with_path + str(frame_number) + '.png'
                    frame = cv2.imdecode(np.fromfile(frame_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    for point in points:
                        self.savePointFromFrame(point, frame, i)
                        i += 1

    def savePointFromFrame(self, point, frame, image_number):
        if frame is None:
            return

        height, width = frame.shape[:2]
        x = int(point.x * width)
        y = int(point.y * height)
        half = point.width // 2

        cropped_image = frame[y - half:y + half, x - half:x + half]
        result_name = os.path.join(self.dataset_path, str(image_number) + '.png')
        is_success, im_buf_arr = cv2.imencode(".png", cropped_image)
        im_buf_arr.tofile(result_name)
