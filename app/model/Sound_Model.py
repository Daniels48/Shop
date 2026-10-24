from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class SoundPlayer:
    def __init__(self):
        self.player = QMediaPlayer()  # Создаём плеер

    def play_sound(self, file_path):
        url = QUrl.fromLocalFile(file_path)
        self.player.setMedia(QMediaContent(url))
        self.player.setVolume(50)  # Громкость (0-100)
        self.player.play()

    def play_error(self):
        path = r"/error.mp3"
        self.play_sound(path)
