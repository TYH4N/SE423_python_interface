import time
from pygame import mixer


mixer.init()
mixer.music.load("test_music.mp3")
mixer.music.play()
while mixer.music.get_busy():  # wait for music to finish playing
    time.sleep(1)