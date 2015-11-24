#!/usr/bin/python3

# cursor hotspot configuration
# TEST load_text -> print when rendering new font and new text
#   and check while going to GameScene and back, OptionsScene and back
# TEST quit methods from main() -> Terminate() not needed?
# script to rename every resource to all lowercase letters
# "are you sure, you want to quit" window as child process, which returns bool

import os
import sys
import pygame

_font_dir = "fonts"
_image_dir = "images"

_sound_lib = {}
_music_lib = {}
_image_lib = {}
_font_lib = {}
_text_lib = {}

_key_lib = {
    "left":  pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump":  pygame.K_UP,
    "duck":  pygame.K_DOWN
}
#http://www.psyclops.com/tools/rgb/
_color_lib = {
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

menu_title = "Bunny hop"
menu_items = (menu_title, "Start game", "Options", "Quit")
menu_actions = (("",""), ("SwitchToScene", "GameScene"), ("SwitchToScene", "OptionsScene"), ("Terminate", ""))
option_title = "Options"
option_items = (option_title, "Resolution", "Fullscreen", "Keys", "Mute sounds")
screen = ""

def load_media(path, library):
    path = path.lower().replace('/', os.sep).replace('\\', os.sep)
    media = library.get(path)
    if media == None:
        if library is _sound_lib:
            media = pygame.mixer.Sound(path)
        elif library is _music_lib:
            media = pygame.mixer.music.load(path)
        elif library is _image_lib:
            media = pygame.image.load(path)
        else:
            raise("Unknown media library: ", library)
        library[path] = media
    if library is _sound_lib:
        sound.play()
        return None
    elif library is _music_lib:
        pygame.mixer.music.play()
        return None
    elif library is _image_lib:
        return media
    else:
        raise("Unknown media library: ", library)

def load_sound(path):
    return load_media(path, _sound_lib)

def load_music(path):
    return load_media(path, _music_lib)

def load_image(path):
    return load_media(path, _image_lib)

def load_font(font, size):
    global _font_lib
    key = str(font) + '|' + str(size)
    font_object = _font_lib.get(key, None)
    if font_object == None:
        try:
            font_object = pygame.font.Font(font, size)
        except OSError:
            font_object = pygame.font.SysFont("", size)
            print("Font (",font,") not found! Using system default font.")
        _font_lib[key] = font_object
    return font_object

def load_text(text, font, size, color):
    global _text_lib, _font_dir
    font = os.path.join(_font_dir, font)
    key = '|'.join(map(str, (font, size, color, text)))
    font_rendered = _text_lib.get(key, None)
    if font_rendered == None:
        font_object = load_font(font, size)
        font_rendered = font_object.render(text, True, color)
        _text_lib[key] = font_rendered
    return font_rendered

def get_center(max_size, act_size):
    return max_size // 2 - act_size // 2

class MenuItem:
    def __init__(self, name, font, font_size, font_color, action):
        self.name = name
        self.font = font
        self.font_size = font_size
        self.font_color = font_color

        self.text = load_text(name, self.font, self.font_size, self.font_color)

        self.width = self.text.get_width()
        self.height = self.text.get_height()
        self.posx = 0
        self.posy = 0

        self.action, self.args = action
        
    def SetPos(self, posx, posy):
        self.posx = posx
        self.posy = posy

    def IsMouseHovered(self, mouse_pos):
        mouse_posx, mouse_posy = mouse_pos
        if self.posx <= mouse_posx and self.posx + self.width > mouse_posx and \
           self.posy <= mouse_posy and self.posy + self.height > mouse_posy:
            return True
        return False

class SceneBase:
    def __init__(self):
        self.next = self

    def ProcessInput(self, events, pressed_keys):
        """Receives all events occured since last frame and
           keys being currently pressed. React to them here."""
        print("Forget to override this in the child class!")

    def Update(self):
        """Game logic: updating flags and variables, move sprites."""
        print("Forget to override this in the child class!")

    def Render(self, screen):
        """Update screen, render new frame and show to the user."""
        print("Forget to override this in the child class!")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        sys.exit()

class TitleScene(SceneBase):
    def __init__(self):
        global _color_lib, menu_title, menu_items, screen

        SceneBase.__init__(self)
        pygame.mouse.set_visible(True)

        self.font = "fff_tusj.ttf"
        self.title_font_size = 72
        self.item_font_size = 50
        self.font_color = _color_lib["black"]
        self.items = []
        self.cur_item = None
        
        # For the aesthetical layout, we add a spacing before the title
        # and between the menu options
        spacing = screen.get_height() // 50
        # For the title, the offset is the spacing above it, but for
        # the other menu items, it will be increased with the height
        # of the title and with future spacings which will be put
        # between the menu items
        offset = spacing
        # Exclude the title from the count of menu items
        item_cnt = len(menu_items)-1

        # Create and store menu items
        for index, name in enumerate(menu_items):
            # Render the text for current item
            font_size = self.item_font_size
            if name == menu_title:
                font_size = self.title_font_size
            label = MenuItem(name, self.font, font_size, self.font_color, menu_actions[index])

            # Center horizontally on the screen, and init vertical position
            # with the current offset
            posx = get_center(screen.get_width(), label.width)
            posy = offset
            
            if name == menu_title:
                # Increase offset for other menu items
                offset += label.height + spacing * (item_cnt-1)
            else :
                # The screen height virtually decreased with the offset,
                # the height of each menu item virtually increased with the spacing,
                # and index is decremented, because the title is excluded from indexing
                posy += get_center((screen.get_height() - offset), (item_cnt * (label.height + spacing))) + ((index-1) * (label.height + spacing))
            
            # Update label position and store label
            label.SetPos(posx, posy)
            self.items.append(label)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(GameScene())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label in self.items:
                    if label.IsMouseHovered(pygame.mouse.get_pos()):
                        print(label.action)
                        print(label.args)
                        #func = getattr(TitleScene, label.action)
                        #func(self,label.args)

    def Update(self):
        pass

    def Render(self):
        global _color_lib, screen

        screen.fill(_color_lib["orange"])

        for label in self.items:
            screen.blit(label.text, (label.posx, label.posy))
            pygame.draw.rect(screen, _color_lib["dark_green"], pygame.Rect(label.posx, label.posy, label.width, label.height),1)

class OptionsScene(SceneBase):
    def __init__(self):
        global _color_lib, option_title, option_items, screen

        SceneBase.__init__(self)
        pygame.mouse.set_visible(True)

        self.font = "fff_tusj.ttf"
        self.title_font_size = 72
        self.item_font_size = 36
        self.font_color = _color_lib["grey"]
        self.items = []
        self.cur_item = None

        # Create and store option items
        for index, name in enumerate(option_items):
            # Render the text for current item
            font_size = self.item_font_size
            if name == option_title:
                font_size = self.title_font_size
            label = MenuItem(name, self.font, font_size, self.font_color, "")

            # Calculate position of label on the screen
            posx = get_center(screen.get_width(), label.width)
            posy = get_center(screen.get_height(), (len(option_items) * label.height)) + (index * label.height)
            if name == option_title:
                posy = 0
            # Add a little spacing between the labels
            posy = posy + screen.get_height() // 50

            # Update label position and store label
            label.SetPos(posx, posy)
            self.items.append(label)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                self.SwitchToScene(TitleScene())

    def Update(self):
        pass

    def Render(self):
        global _color_lib, screen

        screen.fill(_color_lib["forest"])

class GameScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        pygame.mouse.set_visible(False)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                self.SwitchToScene(TitleScene())

    def Update(self):
        pass

    def Render(self):
        global _color_lib, screen

        screen.fill(_color_lib["blue"])

def main(width, height, fps):
    global screen

    pygame.init()

    # Create new cursor from 'cursor_string', where the hotspot is (23,0)
    cursor_string = (
        "            XXXX   XXXX ",
        "           XX..XX XX..XX",
        "           XX...XXX...XX",
        "           XX....XX...XX",
        "            XX...XX..XX ",
        "              XX.XXXXX  ",
        "          XXXXXXXX..XXX ",
        "         XX.XXXXXX....XX",
        "        XXX...XXXXX...XX",
        "       XXX.....XX XX..XX",
        "       XX.......XX  XXX ",
        "      XX........XX      ",
        "     XX.........XX      ",
        "     XX........XXX      ",
        "    XX........XXX       ",
        "   XX........XXX        ",
        "   XX.......XXX         ",
        "  XX......XXX           ",
        " XX......XXX            ",
        " XX....XXX              ",
        "XX....XXX               ",
        "XX..XXX                 ",
        "XXXXXX                  ",
        "XXXX                    ")
    cursor, mask = pygame.cursors.compile(cursor_string, 'X', '.', 'O')
    cursor_size = len(cursor_string[0]), len(cursor_string)
    pygame.mouse.set_cursor(cursor_size, (0,23), cursor, mask)

    # Create graphical window
    pygame.display.set_caption("Bunny hop")
    pygame.display.set_icon(load_image(os.path.join(_image_dir,"bunny_256.png")))
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    active_scene = TitleScene()

    while True:
        filtered_events = []
        pressed_keys = pygame.key.get_pressed()

        # Process quit requests, collect all other requests
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and \
             (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])):
                return
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render()

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)

# Execute main function only after the whole script was parsed
if __name__ == "__main__":
    main(640, 360, 60)
