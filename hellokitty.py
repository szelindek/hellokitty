#!/usr/bin/python3
r"""

util_chimpy:
    derive from Sprite class
    create RenderPlain==Group class -> sprite handling easier
    use Rect class for (posx, posy, width, height)
util_functions:
    keyboard control for menu

defaults for optional parameters (like screen for Update()

react to pressed_keys instead of KEYDOWN -> continouos movement
solve race situation (where left and right pressed the same time)
    do not stop current movement until current key is released

store image of the background
movement:
    replace all to-be-moved objects on screen with background (blitting)
    calculate object movement
    blit all moving objects at their new position
    use display.update(rect_list_to_update) to refresh only changed parts of the screen

detect display resolution and collect possible resolutions:
    pygame.display.list_modes() -> all possible resolutions
    pygame.display.Info() -> display info object
        wm: if false, then only fullscreen is allowed (no windowed mode)
        current_w, current_h: current resolution
    pygame.display.get_wm_info() -> windowed mode info list

range_lo and range_hi for printing lists: range_lo == offset

include sub_main content here as function, and use ask.py to pop up message and
    enable keys (enter selects active answer, default active yes, can move with keys)

Physics:
    RK4 integrator
    fixed time-step
    inputs apply forces

TEST:


"""

import os
import sys
import pygame
import subprocess
from mycommon import *

# Items of the main menu: tuples of label of the menu item and the scene
# connected to it
_menu_items = (("Bunny hop", "TitleScene"), ("Start game", "GameScene"),
               ("Options", "OptionsScene"), ("Quit", ""))
_option_items = ("Options", "Resolution", "Fullscreen", "Keys", "Mute sounds")

class MenuItem:
    def __init__(self, name, font=None, font_size=21,
                 font_color=color_lib["white"], action=""):
        self.name = name
        self.font = font
        self.font_size = font_size
        self.font_color = font_color

        self.text = load_text(name, self.font, self.font_size, self.font_color)

        self.width = self.text.get_width()
        self.height = self.text.get_height()
        self.posx = 0
        self.posy = 0

        self.action = action

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
    def __init__(self, screen):
        pass

    def ProcessInput(self, events, pressed_keys):
        """Receives all events occured since last frame and
           keys being currently pressed. React to them here."""
        print("Forget to override this in the child class!")
        return self.__class__.__name__

    def Update(self, screen):
        """Game logic: updating flags and variables, move sprites."""
        print("Forget to override this in the child class!")

    def Render(self, screen):
        """Update screen, render new frame and show to the user."""
        print("Forget to override this in the child class!")

class TitleScene(SceneBase):
    def __init__(self, screen):
        global color_lib, _menu_items

        SceneBase.__init__(self, screen)
        pygame.mouse.set_visible(True)

        self.font = "fff_tusj.ttf"
        self.title_font_size = 72
        self.item_font_size = 50
        self.font_color = color_lib["black"]
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
        item_cnt = len(_menu_items)-1

        # Create and store menu items
        for index, element in enumerate(_menu_items):
            name = element[0]
            scene = element[1]

            # Render the text for current item
            font_size = self.item_font_size
            if index == 0:
                font_size = self.title_font_size
            label = MenuItem(name, self.font, font_size, self.font_color, scene)

            # Center horizontally on the screen, and init vertical position
            # with the current offset
            posx = get_center(screen.get_width(), label.width)
            posy = offset

            if index == 0:
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
                # Move to the game scene as a test
                return "GameScene"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label in self.items:
                    if label.IsMouseHovered(pygame.mouse.get_pos()):
                        return label.action
        return self.__class__.__name__

    def Update(self, screen):
        pass

    def Render(self, screen):
        global color_lib

        screen.fill(color_lib["orange"])

        for label in self.items:
            screen.blit(label.text, (label.posx, label.posy))

class OptionsScene(SceneBase):
    def __init__(self, screen):
        SceneBase.__init__(self, screen)
        pygame.mouse.set_visible(True)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                return "TitleScene"
        return self.__class__.__name__

    def Update(self, screen):
        pass

    def Render(self, screen):
        global color_lib

        screen.fill(color_lib["forest"])

        label = MenuItem("The cake is a lie!", "fff_tusj.ttf", 72, color_lib["white"])
        posx = get_center(screen.get_width(), label.width)
        posy = get_center(screen.get_height(), label.height)
        label.SetPos(posx, posy)
        screen.blit(label.text, (label.posx, label.posy))

class Bunny:
    def __init__(self, posx, posy):
        global image_dir

        scaled_width = 40

        self.look = load_image(os.path.join(image_dir,"bunny_look.png"))
        self.look = pygame.transform.flip(self.look, True, False)
        self.facing_right = True
        self.look = pygame.transform.smoothscale(self.look, (scaled_width,int(1.5*scaled_width)))
        self.posx = posx
        self.posy = posy
        self.width = self.look.get_width()
        self.height = self.look.get_height()

    def move(self, posx_delta, posy_delta):
        self.posx += posx_delta
        self.posy += posy_delta

        # If moving left but facing right, or moving right but facing left,
        # then flip the bunny look, to face in the direction of the movement
        if (posx_delta < 0 and self.facing_right == True) or \
           (posx_delta > 0 and self.facing_right == False):
            self.look = pygame.transform.flip(self.look, True, False)
            self.facing_right = not self.facing_right

    def force_boundaries(self, screen):
        if self.posx < 0:
            self.posx = 0
        elif self.posx > screen.get_width() - self.width:
            self.posx = screen.get_width() - self.width
        if self.posy < 0:
            self.posy = 0
        elif self.posy > screen.get_height() - self.height:
            self.posy = screen.get_height() - self.height

class GameScene(SceneBase):
    def __init__(self, screen):
        SceneBase.__init__(self, screen)
        pygame.mouse.set_visible(False)

        self.bunny = Bunny(screen.get_width() // 20,
                           screen.get_height() - (screen.get_height() // 3))

    def ProcessInput(self, events, pressed_keys):
        global key_lib

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Move back to title scene when escape is pressed
                return "TitleScene"
            elif event.type == pygame.KEYDOWN and event.key == key_lib["left"]:
                self.bunny.move(-10,0)
            elif event.type == pygame.KEYDOWN and event.key == key_lib["right"]:
                self.bunny.move(10,0)
            elif event.type == pygame.KEYDOWN and event.key == key_lib["jump"]:
                self.bunny.move(0,-10)
            elif event.type == pygame.KEYDOWN and event.key == key_lib["duck"]:
                self.bunny.move(0,10)
        return self.__class__.__name__

    def Update(self, screen):
        self.bunny.force_boundaries(screen)

    def Render(self, screen):
        global color_lib

        screen.fill(color_lib["royalblue"])
        pygame.draw.rect(screen, color_lib["neon"], pygame.Rect(self.bunny.posx, self.bunny.posy, self.bunny.width, self.bunny.height),1)
        screen.blit(self.bunny.look, (self.bunny.posx, self.bunny.posy))

def ask_question(question):
    """
    try:
        subprocess.run(["python","ask.py"],
                       input=question.encode("utf-8"),
                       check=True)
    except subprocess.CalledProcessError:
        return True
    
    return False
    """
        
def main(width, height, fps):
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
    pygame.display.set_icon(load_image(os.path.join(image_dir,"bunny_256.png")))
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    active_scene = TitleScene(screen)
    
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

        next_scene = active_scene.ProcessInput(filtered_events, pressed_keys)
        if next_scene == "":
            # If the returned scene name is empty, ask quit for approval
            #if ask_question("Do you really want to quit?"):
            break
        elif next_scene == active_scene.__class__.__name__ :
            # Don't need to change scene, we can continue normally
            active_scene.Update(screen)
            active_scene.Render(screen)
        else:
            # Initialize new scene from string
            active_scene = globals()[next_scene](screen)

        pygame.display.flip()
        clock.tick(fps)

# Execute main function only after the whole script was parsed
if __name__ == "__main__":
    main(640, 360, 60)
