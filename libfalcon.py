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

############################### UTILITY FUNCTIONS ##############################

def inverse_dict(dict):
    return {dict[k] : k for k in dict}

# Calculate center from two inputs, returned value is minimum zero
def get_center(max_size, act_size):
    return max((max_size // 2 - act_size // 2), 0)

############################### SHARED LIBRARIES ###############################

font_dir = "fonts"
image_dir = "images"

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
    "indigo":       (75, 0, 130),
    "dark_orange":  (200,100,0)
}

default_font = "fff_tusj.ttf"
default_font_size = 50
default_header_font_size = 72
default_font_color = color_lib["black"]

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
    "upleft":    3,
    "upright":   6
}

mov_lib_r = inverse_dict(mov_lib)

key_lib = {
    "left":  pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up":    pygame.K_UP
}

key_lib_r = inverse_dict(key_lib)

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

class MenuElem:
    def __init__(self, name, font=default_font, font_size=default_font_size,
                 font_color=default_font_color, action=""):

        self.name = name
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.action = action

        self.text = load_text(name, self.font, self.font_size, self.font_color)

        self.width = self.text.get_width()
        self.height = self.text.get_height()
        self.posx = 0
        self.posy = 0

    def SetPos(self, posx, posy):
        self.posx = posx
        self.posy = posy

    def IsMouseHovered(self, mouse_pos):
        mouse_posx, mouse_posy = mouse_pos
        if self.posx <= mouse_posx and self.posx + self.width > mouse_posx and \
           self.posy <= mouse_posy and self.posy + self.height > mouse_posy:
            return True
        return False

class MenuBase:
    def __init__(self, screen, header_list, item_list, font=default_font,
                 font_size=default_font_size, header_font_size=default_header_font_size,
                 font_color=default_font_color, spacing_ratio=50):

        self.font = font
        self.font_size = font_size
        self.header_font_size = header_font_size
        self.font_color = font_color
        self.headers = []
        self.items = []
        self.cur_item = None
        self.cur_rect = None

        # For the aesthetical layout, we add a spacing before the headers
        # and between the menu options as well
        spacing = self.window.h // spacing_ratio
        # For the headers, the offset is the spacing above them, but for
        # the other menu items, it will be increased with the height
        # of the headers and with future spacings which will be put
        # between the menu items
        offset = spacing

        # Create and store menu items
        for name in header_list:
            # Render the text for current item
            label = MenuElem(name, self.font, self.header_font_size, self.font_color)

            # Center horizontally on the screen, and init vertical position
            # with the current offset
            posx = get_center(self.window.w, label.width) + self.window.x
            posy = offset

            # Update label position
            label.SetPos(posx, posy)

            # Increase offset for non-header menu items with height of the header
            offset += label.height

            # Store
            self.headers.append(label)

        # Create and store menu items
        for index, item in enumerate(item_list):
            name = item[0]
            action = item[1]

            # Render the text for current item
            label = MenuElem(name, self.font, self.font_size, self.font_color, action)

            # Center horizontally on the screen, and init vertical position
            # with the current offset
            posx = get_center(self.window.w, label.width) + self.window.x
            # The screen height virtually decreased with the offset,
            # the height of each menu item virtually increased with the spacing,
            # and index is decremented, because the title is excluded from indexing
            posy = offset + \
                get_center((self.window.h - offset),(len(item_list) * (label.height + spacing))) + \
                (index * (label.height + spacing)) + self.window.y

            # Update label position
            label.SetPos(posx, posy)

            # Increase offset for next items
            offset += spacing

            # Store
            self.items.append(label)

    def BlitMenu(self, screen, background_color):
        screen.fill(background_color, self.window)
        for label in self.headers:
            screen.blit(label.text, (label.posx, label.posy))
        for label in self.items:
            screen.blit(label.text, (label.posx, label.posy))
        if self.cur_rect != None:
            pygame.draw.rect(screen, color_lib["black"], self.cur_rect, 1)

    def HandleKeyboard(self, screen, key):
        if key == pygame.K_ESCAPE:
            return "TitleScene"
        elif (key == pygame.K_SPACE or key == pygame.K_RETURN) and \
        self.cur_item != None:
            return self.items[self.cur_item].action
        elif key == pygame.K_UP or key == pygame.K_DOWN:
            # Move the item selection
            if key == pygame.K_UP:
                if self.cur_item == None or self.cur_item == 0:
                    self.cur_item = len(self.items) - 1
                elif self.cur_item > 0:
                    self.cur_item -= 1
            elif key == pygame.K_DOWN:
                if self.cur_item == None or self.cur_item == len(self.items) - 1:
                    self.cur_item = 0
                elif self.cur_item < len(self.items) - 1:
                    self.cur_item += 1
            # Update the rect which is drawn around the currently selected item
            self.cur_rect = pygame.Rect(self.items[self.cur_item].posx,
                self.items[self.cur_item].posy,
                self.items[self.cur_item].width,
                self.items[self.cur_item].height)

        return self.__class__.__name__

    def HandleMouse(self, button):
        if button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for label in self.items:
                if label.IsMouseHovered(mouse_pos):
                    return label.action

        return self.__class__.__name__

class SpriteBase(pygame.sprite.Sprite):
    def __init__(self, look_image, scaling, posx, posy, screen):
        pygame.sprite.Sprite.__init__(self)

        # Load image to get a fancy look
        self.look = load_image(os.path.join(image_dir, look_image))

        # Scale the look depending on the display resolution
        ratio = self.look.get_height() / self.look.get_width()
        scaled_width = screen.get_width() // scaling
        self.look = pygame.transform.smoothscale(self.look,
                    (scaled_width, int(ratio*scaled_width)))

        # Get rect!
        # The stored posy (upper-left corner) is derived from the input argument
        # posy, which is the bottom-left corner. The upper-left corner posy.
        # can't be given as input because the height of the sprite is not known
        # in advance!
        self.rect = pygame.Rect(posx, posy-self.look.get_height(),
                    self.look.get_width(), self.look.get_height())

class SceneBase:
    def __init__(self, screen, window):
        self.window = window
        pygame.mouse.set_visible(True)
        pygame.key.set_repeat()

    def ProcessInput(self, screen, events, pressed_keys):
        """Receives all events occured since last frame and
           keys being currently pressed. React to them here."""
        print("Forget to override this in the child class!")
        return self.__class__.__name__

    def GenerateOutput(self, screen):
        """Update screen, render new frame and show to the user."""
        print("Forget to override this in the child class!")

################################ CHECK LOAD TYPE ###############################

if __name__ == "__main__":
    print ("LIBFALCON.PY should be imported as a library!!!")
