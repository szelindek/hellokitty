#/usr/bin/python3

import os, pygame

_font_dir = "fonts"
_image_dir = "images"

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

_sound_lib = {}
def play_sound(path):
    global _sound_lib
    path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = _sound_lib.get(path)
    if sound == None:
        sound = pygame.mixer.Sound(path)
        _sound_lib[path] = sound
    sound.play()

_music_lib = {}
def play_music(path):
    global _music_lib
    path = path.replace('/', os.sep).replace('\\', os.sep)
    music = _music_lib.get(path)
    if music == None:
        music = pygame.mixer.music.load(path)
        _music_lib[path] = music
    pygame.mixer.music.play()

_image_lib = {}
def load_image(path):
    global _image_lib
    path = path.lower().replace('/', os.sep).replace('\\', os.sep)
    image = _image_lib.get(path)
    if image == None:
        image = pygame.image.load(path)
        _image_lib[path] = image
    return image

_cached_fonts = {}
def get_font(fonts, size):
    global _cached_fonts
    key = str(fonts) + '|' + str(size)
    font = _cached_fonts.get(key, None)
    if font == None:
        try:
            font = pygame.font.Font(fonts, size)
        except:
            font = pygame.font.SysFont("", size)
            print("Desired font (",fonts,") not found! Using system default font.")
        _cached_fonts[key] = font
    return font

_cached_text = {}
def create_text(text, fonts, size, color):
    global _cached_text, _font_dir
    fonts = os.path.join(_font_dir, fonts)
    key = '|'.join(map(str, (fonts, size, color, text)))
    image = _cached_text.get(key, None)
    if image == None:
        font = get_font(fonts, size)
        image = font.render(text, True, color)
        _cached_text[key] = image
    return image

def get_center(max_size, act_size):
    return max_size // 2 - act_size // 2

pygame_init_called = False
_key_lib = {
    "left":  pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump":  pygame.K_UP,
    "down":  pygame.K_DOWN
}
_color_lib = {
    "white":  (255, 255, 255),
    "black":  (0, 0, 0),
    "red":    (255, 0, 0),
    "green":  (0, 255, 0),
    "blue":   (0, 0, 255),
    "orange": (255, 171, 24)
}
def run_game(width, height, fps, starting_scene):
    pygame.init()
    global pygame_init_called
    pygame_init_called = True

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
    # Create new cursor from 'cursor_string', where the hotspot is (0,0)
    pygame.mouse.set_cursor(cursor_size, (0,0), cursor, mask)

    pygame.display.set_caption("Bunny hop")
    pygame.display.set_icon(load_image(os.path.join(_image_dir,"bunny_256.png")))
    screen = pygame.display.set_mode((width, height))
    #screen = pygame.display.set_mode((width, height),pygame.FULLSCREEN)

    clock = pygame.time.Clock()

    active_scene = starting_scene

    print ("Starting while loop")

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
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)

class TitleScene(SceneBase):
    title_font = "fff_tusj.ttf"
    text = ""

    def __init__(self):
        SceneBase.__init__(self)
        global pygame_init_called
        if pygame_init_called:
            pygame.mouse.set_visible(True)
        print("Inited TitleScene")

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(GameScene())

    def Update(self):
        pass

    def Render(self, screen):
        global _color_lib, pygame_init_called
        screen.fill(_color_lib["orange"])
        if pygame_init_called:
            self.text = create_text("Bunny hop", self.title_font, 72, _color_lib["black"])
            screen.blit(self.text,(get_center(screen.get_width(), self.text.get_width()), 0))

class GameScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        pygame.mouse.set_visible(False)
        print("Inited GameScene")

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                self.SwitchToScene(TitleScene())

    def Update(self):
        pass

    def Render(self, screen):
        global _color_lib
        screen.fill(_color_lib["blue"])


# Execute main function only after the whole script was parsed
run_game(640, 360, 60, TitleScene())
