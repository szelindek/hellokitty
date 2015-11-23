#!/usr/bin/python3

# cursor hotspot configure
# test load_text, try-except: only except for defined exceptions!
# script to rename every resource to all lowercase letters
#

import os, pygame

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
_color_lib = {
    "white":  (255, 255, 255),
    "black":  (0, 0, 0),
    "red":    (255, 0, 0),
    "green":  (0, 255, 0),
    "blue":   (0, 0, 255),
    "orange": (255, 171, 24)
}

menu_title = "Bunny hop"
menu_items = (menu_title, "Start game", "Options", "Quit")
screen = ""

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
        self.SwitchToScene(None)

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
        except:
            font_object = pygame.font.SysFont("", size)
            print("Desired font (",font,") not found! Using system default font.")
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

class TitleScene(SceneBase):
    def __init__(self):
        global _color_lib, menu_title, menu_items, screen

        SceneBase.__init__(self)
        pygame.mouse.set_visible(True)

        self.font = "fff_tusj.ttf"
        self.color = _color_lib["black"]
        self.title_size = 72
        self.item_size = 50
        self.items = []

        # Create and store menu items
        screen_tenth = screen.get_height() // 50
        for index, item in enumerate(menu_items):
            needed_size = self.item_size
            if item == menu_title:
                needed_size = self.title_size

            self.text = load_text(item, self.font, needed_size, self.color)

            width = self.text.get_width()
            height = self.text.get_height()

            posx = get_center(screen.get_width(), width)
            # "len(menu_items) * height": total height of text block
            posy = get_center(screen.get_height(), (len(menu_items) * height)) + (index * height)
            if item == menu_title:
                posy = 0

            self.items.append([item, self.text, (width, height), (posx, posy + screen_tenth)])

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(GameScene())

    def Update(self):
        pass

    def Render(self):
        global _color_lib, screen

        screen.fill(_color_lib["orange"])

        for name, label, (width, height), (posx, posy) in self.items:
            screen.blit(label, (posx, posy))

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
    global menu_items, screen

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
    pygame.mouse.set_cursor(cursor_size, (23,0), cursor, mask)

    # Create graphical window
    pygame.display.set_caption("Bunny hop")
    pygame.display.set_icon(load_image(os.path.join(_image_dir,"bunny_256.png")))
    screen = pygame.display.set_mode((width, height))
    #screen = pygame.display.set_mode((width, height),pygame.FULLSCREEN)

    clock = pygame.time.Clock()
    active_scene = TitleScene()

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.Terminate()
                break
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render()

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)

# Execute main function only after the whole script was parsed
main(640, 360, 60)
