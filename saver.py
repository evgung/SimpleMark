# номер последнего редактируемого кадра, название изображения (название видео + _ )
# (изображения имеют вид: название видео + _ + номер + .png)
# ДО МЕНЯ ТУТ ДОШЛО, ЧТО ДАЛЬШЕ ДЛЯ ПОЛУЧЕНИЯ САМИХ ДАТАСЕТОВ БУДКТ НУЖНЫ ТАКЖЕ ИСХОДНЫЕ ВЫСОТА И ШИРИНА
# Добавь их, если у тебя получение результата будет в этом же классе
# метод, который получает список точек Point и номер кадра, и сохраняет все точки в соответствующий файл


# переносить видео в корневую папку при желании пользователя
# возможность взять исходное количество кадров
# возможность возвращаться к разбиению видео
# (тогда нужно сохранять путь к видео и номер последнего кадра/прошедшее время, кол-во кадров в секунду)

import os
import pickle

class Saver:

    def __init__(self, project_path):
        self.project_path = project_path
        self.config_file = os.path.join(project_path, "config.pkl")
        self.info_path = os.path.join(project_path, "info")

    def saveProject(self, last_frame_number, path_to_video, last_extracted_frame_number, fps):
        properties = {
            "last_frame_number": last_frame_number,
            "path_to_video": path_to_video,
            "last_extracted_frame_number": last_extracted_frame_number,
            "fps": fps
        }

        with open(self.config_file, 'wb') as config:
            pickle.dump(properties, config)

    # points - массив объектов класса Point
    def saveFramePoints(self, frame_number, points):
        with open(os.path.join(self.info_path, str(frame_number)), 'wb') as frame_file:
            pickle.dump(points, frame_file)
