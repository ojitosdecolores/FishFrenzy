import pygame

# Initializes Pygame mixer
def init_music():
    pygame.mixer.init()

# Load and play background music
def play_music(file_path, loop=-1, start_time=0.0):
    pygame.mixer.music.load(file_path)  
    pygame.mixer.music.play(loop, start_time) 

# Set volume
def set_music_volume(volume=1.0):
    pygame.mixer.music.set_volume(volume)  # Set the volume (range: 0.0 to 1.0)

# Stop
def stop_music():
    pygame.mixer.music.stop()

# Pause
def pause_music():
    pygame.mixer.music.pause()

# Unpause
def unpause_music():
    pygame.mixer.music.unpause()
