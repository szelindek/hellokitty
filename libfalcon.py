r"""
Content:
    Shared libraries, mainly for objects loaded from media files
    Media loading functions, handle file system and store objects in shared libs
    Class templates, from which specialized classes derive
    Utility functions with general purpose
"""

################################### IMPORTS ####################################

import os
import pygame

############################### SHARED LIBRARIES ###############################

def inverse_dict(dict):
    return {dict[k] : k for k in dict}

font_dir = "fonts"
image_dir = "images"

default_font = "fff_tusj.ttf"

sound_lib = {}
music_lib = {}
image_lib = {}
font_lib = {}
text_lib = {}

mov_lib = {
    "stand": 0,
    "left":  1,
    "up":    2,
    "right": 4,
    "down":  8,
    "upleft":    3,
    "upright":   6,
    "downleft":  9,
    "downright": 12
}

mov_lib_r = inverse_dict(mov_lib)

key_lib = {
    "left":  pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up":    pygame.K_UP,
    "down":  pygame.K_DOWN
}

key_lib_r = inverse_dict(key_lib)

#http://www.psyclops.com/tools/rgb/
color_lib = {
    "black":        (0, 0, 0),
    "dark_red":     (128, 0, 0),
    "red":          (255, 0, 0),
    "dark_green":   (0, 128, 0),
    "green":        (0, 255, 0),
    "dark_blue":    (0, 0, 128),
    "blue":         (0, 0, 255),
    "dark_yellow":  (128, 128, 0),
    "yellow":       (255, 255, 0),
    "light_yellow": (255, 255, 128),
    "dark_pink":    (128, 0, 128),
    "pink":         (255, 0, 255),
    "light_pink":   (255, 128, 255),
    "dark_cyan":    (0, 128, 128),
    "cyan":         (0, 255, 255),
    "light_cyan":   (128, 255, 255),
    "grey":         (128, 128, 128),
    "white":        (255, 255, 255),
    "orange":       (255, 128, 0),
    "magenta":      (255, 0, 128),
    "neon":         (128, 255, 0),
    "spring":       (0, 255, 128),
    "purple":       (128, 0, 255),
    "royalblue":    (0, 128, 255),
    "light_purple": (128, 128, 255),
    "light_neon":   (128, 255, 128),
    "peach":        (255, 128, 128),
    "beige":        (245, 245, 220),
    "blueviolet":   (138, 43, 226),
    "brown":        (180, 80, 40),
    "crimson":      (220, 20, 60),
    "darkolive":    (85, 107, 47),
    "darkorchid":   (153, 50, 204),
    "darkviolet":   (148, 0, 211),
    "deeppink":     (255, 20, 147),
    "skyblue":      (0, 191, 255),
    "forest":       (34, 139, 34),
    "indigo":       (75, 0, 130)
}

########################### MEDIA LOADING FUNCTIONS ############################

class LibraryError(Exception):
    pass

def load_media(path, library):
    path = path.lower().replace('/', os.sep).replace('\\', os.sep)
    media = library.get(path)
    if media == None:
        try:
            if library is sound_lib:
                media = pygame.mixer.Sound(path)
            elif library is music_lib:
                media = pygame.mixer.music.load(path)
            elif library is image_lib:
                # Load image and convert it to the same format as the display
                media = pygame.image.load(path)
            else:
                raise LibraryError("Unsupported library!")
        except pygame.error as message:
            print ("Cannot load media:", path)
            raise SystemExit(message)
        # Cache media object
        library[path] = media

    if library is sound_lib:
        sound.play()
        return None
    elif library is music_lib:
        pygame.mixer.music.play()
        return None
    elif library is image_lib:
        # If we have already initialized a screen, convert the image to the
        # actual screen pixel format (for faster blitting)
        if pygame.display.get_surface() != None:
            media = media.convert_alpha()
        return media
    else:
        raise LibraryError("Unsupported library!")

def load_sound(path):
    return load_media(path, sound_lib)

def load_music(path):
    return load_media(path, music_lib)

def load_image(path):
    return load_media(path, image_lib)

def load_font(font, size):
    global font_lib
    key = str(font) + '|' + str(size)
    font_object = font_lib.get(key, None)
    if font_object == None:
        try:
            font_object = pygame.font.Font(font, size)
        except OSError:
            font_object = pygame.font.SysFont("", size)
            print("Font (",font,") not found! Using system default font.")
        font_lib[key] = font_object
    return font_object

def load_text(text, font, size, color):
    global text_lib, font_dir
    font = os.path.join(font_dir, font)
    key = '|'.join(map(str, (font, size, color, text)))
    font_rendered = text_lib.get(key, None)
    if font_rendered == None:
        font_object = load_font(font, size)
        font_rendered = font_object.render(text, True, color)
        text_lib[key] = font_rendered
    return font_rendered

################################ CLASS TEMPLATES ###############################

class SceneBase:
    def __init__(self, screen):
        pygame.mouse.set_visible(True)

    def ProcessInput(self, events, pressed_keys):
        """Receives all events occured since last frame and
           keys being currently pressed. React to them here."""
        print("Forget to override this in the child class!")
        return self.__class__.__name__

    def Update(self, screen):
        """Game logic: updating flags and variables, move objects."""
        print("Forget to override this in the child class!")

    def Render(self, screen):
        """Update screen, render new frame and show to the user."""
        print("Forget to override this in the child class!")

############################### UTILITY FUNCTIONS ##############################



# Calculate center from two inputs, returned value is minimum zero
def get_center(max_size, act_size):
    return max((max_size // 2 - act_size // 2), 0)
