import os
import pickle


class Saver:

    def __init__(self, project_path):
        self.project_path = project_path
        self.config_file = os.path.join(project_path, "config.pkl")
        self.info_path = os.path.join(project_path, "info")
        os.makedirs(self.info_path, exist_ok=True)

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

        if len(points) == 0 and os.path.exists(info_file):
            os.remove(info_file)
            return

        with open(info_file, 'wb') as frame_file:
            pickle.dump(points, frame_file)
