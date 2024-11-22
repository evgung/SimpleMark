import os
import pickle


class Loader:

    def __init__(self, project_path):
        self.project_path = project_path
        self.config_file = os.path.join(project_path, "config.pkl")
        self.info_path = os.path.join(project_path, "info")

    # Возвращает словарь со свойствами:
    # "last_frame_number" - номер последнего открытого кадра
    # "path_to_video" - путь к видео
    # "last_extracted_frame_number" - номер кадра, на котором остановилась обработка видео
    #                                 (на случай, если получится продолжить обработку)
    # "fps" - количество кадров в секунду
    def getProjectProperties(self):
        try:
            with open(self.config_file, 'rb') as config:
                properties = pickle.load(config)
            return properties
        except FileNotFoundError:
            # Если проект был закрыт без сохранения
            return {
                "last_frame_number": 0,
                "path_to_video": None,
                "last_extracted_frame_number": None,
                "fps": None,
                "image_name": "",
                "image_path": ""
            }

    # Возвращает список объектов класса Point
    # Если этот кадр еще не был размечен, возвращает пустой список
    def getFramePoints(self, frame_number):
        try:
            with open(os.path.join(self.info_path, str(frame_number)), 'rb') as frame_file:
                points = pickle.load(frame_file)
            return points
        except FileNotFoundError:
            return []
